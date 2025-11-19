from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor
from transformers.generation import GenerationConfig
import torch
import base64
from zhipuai import ZhipuAI
from io import BytesIO
from urllib.request import urlopen
import librosa
from openai import OpenAI

import warnings
warnings.filterwarnings("ignore")

# First install the required library
# Run this command in terminal:
# pip install google-generativeai

# Then modify the imports section:


class GeminiAudio:
    """
    gemini-2.0-flash
    gemini-1.5-flash
    gemini-1.5-pro

    gemini-1.5-flash-8b（可不测）
    """

    def __init__(self, model_name, api_key):
        self.model_name = model_name
        configure(api_key=api_key)
        self.model = GenerativeModel(model_name)

    def chat(self, prompt, audio_path):
        response = self.model.generate_content(
            contents=[
                prompt,
                audio_path,  # The library handles file loading automatically
            ]
        )
        return response.text


class GPT4oAudioPreview:
    model_name = 'gpt-4o-audio-preview'

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.init_clinet()

    def init_clinet(self):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    def chat(self, prompt, audio_path):
        with open(audio_path, "rb") as audio_file:
            mp3_data = audio_file.read()
        encoded_string = base64.b64encode(mp3_data).decode('utf-8')

        completion = self.client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "alloy", "format": "mp3"},
            temperature=0.01,
            messages=[
                {
                    "role": "user",
                    "content": [
                        { 
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded_string,
                                "format": "mp3"
                            }
                        }
                    ]
                },
            ]
        )
        return completion.choices[0].message.audio.transcript

class GLM4Audio:
    model_name = 'glm-4-voice'

    def __init__(self, api_key):
        self.api_key = api_key
        self.init_clinet()

    def init_clinet(self):
        self.client = ZhipuAI(api_key=self.api_key)
    
    def base64_encode_audio(self, audio_path):
        with open(audio_path, "rb") as audio_file:
            mp3_data = audio_file.read()
        return base64.b64encode(mp3_data).decode('utf-8')

    def chat(self, prompt, audio_path):
        audio_base64 = self.base64_encode_audio(audio_path)
        response = self.client.chat.completions.create(
            model="glm-4-voice",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format":"mp3"
                            }
                        }
                    ]
                },
            ],
            max_tokens=1024,
            stream=False, 
            temperature=0.01
        )   
        return response.choices[0].message.content
    
class Qwen1Audio:
    model_name = 'Qwen1Audio'

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.init_model()

    def init_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, device_map="cuda:0", trust_remote_code=True, bf16=True).eval()
    
    def chat(self, prompt, audio_path):
        query = self.tokenizer.from_list_format([
            {'audio': audio_path}, 
            {'text': prompt},
        ])
        response, history = self.model.chat(self.tokenizer, query=query, history=None, temperature=0.01)
        return response
    
class Qwen2Audio:
    model_name = 'Qwen2Audio'
    
    def __init__(self, model_path=None, system='You are a helpful Assistant.'):
        self.model_path = model_path
        self.system = system
        self.init_model()

    def init_model(self):
        self.processor = AutoProcessor.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = Qwen2AudioForConditionalGeneration.from_pretrained(self.model_path, torch_dtype=torch.bfloat16, device_map="cuda:0")

    def chat(self, prompt, audio_path):
        conversation = [
            {'role': 'system', 'content': self.system}, 
            {"role": "user", "content": [
                {"type": "audio", "audio": audio_path},
                {"type": "text", "text": prompt},
            ]},
        ]
        text = self.processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        audios = []
        for message in conversation:
            if isinstance(message["content"], list):
                for ele in message["content"]:
                    if ele["type"] == "audio":
                        if "audio_url" in ele:
                            audios.append(librosa.load(BytesIO(urlopen(ele['audio_url']).read()), sr=self.processor.feature_extractor.sampling_rate)[0])
                        elif "audio" in ele:
                            audios.append(librosa.load(ele['audio'], sr=self.processor.feature_extractor.sampling_rate)[0])
        inputs = self.processor(text=text, audios=audios, return_tensors="pt", padding=True, sampling_rate=16000).to('cuda:0')
        inputs.input_ids = inputs.input_ids

        generate_ids = self.model.generate(**inputs, max_length=4096, temperature=0.01)
        generate_ids = generate_ids[:, inputs.input_ids.size(1):]

        response = self.processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        return response
        
class Qwen2AudioBase:
    model_name = 'Qwen2Audio'
    
    def __init__(self, model_path=None, system='You are a helpful Assistant.'):
        self.model_path = model_path
        self.system = system
        self.init_model()

    def init_model(self):
        self.processor = AutoProcessor.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = Qwen2AudioForConditionalGeneration.from_pretrained(self.model_path, torch_dtype=torch.bfloat16, device_map="cuda:0")

    def chat(self, prompt, audio_path):
        conversation = [
            {'role': 'system', 'content': self.system}, 
            {"role": "user", "content": [
                {"type": "audio", "audio": audio_path},
                {"type": "text", "text": prompt},
            ]},
        ]
        text = self.processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        audios = []
        for message in conversation:
            if isinstance(message["content"], list):
                for ele in message["content"]:
                    if ele["type"] == "audio":
                        if "audio_url" in ele:
                            audios.append(librosa.load(BytesIO(urlopen(ele['audio_url']).read()), sr=self.processor.feature_extractor.sampling_rate)[0])
                        elif "audio" in ele:
                            audios.append(librosa.load(ele['audio'], sr=self.processor.feature_extractor.sampling_rate)[0])
        inputs = self.processor(text=text, audios=audios, return_tensors="pt", padding=True, sampling_rate=16000).to('cuda:0')
        inputs.input_ids = inputs.input_ids

        generate_ids = self.model.generate(**inputs, max_length=4096, temperature=0.01)
        generate_ids = generate_ids[:, inputs.input_ids.size(1):]

        response = self.processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        return response
        
# Add to the existing imports at the top
# from speechbrain.inference.multimodal import LTU_AS


# In the existing model class after adding new class
# class LTUAS:
#     model_name = 'LTU-AS'
    
#     def __init__(self, model_path=None, system='You are a helpful Assistant.'):
#         self.model_path = model_path or "speechbrain/speech-llm-LTU-AS-openasqa"
#         self.system = system
#         self.init_model()

#     def init_model(self):
#         # 初始化语音识别模型
#         self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
#         self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
#         # 初始化LTU-AS模型
#         self.ltu_as = LTU_AS.from_hparams(
#             source=self.model_path,
#             run_opts={"device": self.device.split(':')[0]}
#         )
        
#         # 初始化ASR模型（保持原有实现）
#         self.asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(
#             "openai/whisper-large-v3",
#             torch_dtype=self.torch_dtype,
#             low_cpu_mem_usage=True,
#             use_safetensors=True
#         ).to(self.device)
        
#         self.processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")
        
#         # 初始化LTU-AS模型
#         self.ltu_as = LTU_AS.from_hparams(
#             source="speechbrain/speech-llm-LTU-AS-openasqa",
#             run_opts={"device": self.device.split(':')[0]}  # 自动适配设备
#         )
        
#         # 初始化语音识别管道
#         self.pipe = pipeline(
#             "automatic-speech-recognition",
#             model=self.asr_model,
#             tokenizer=self.processor.tokenizer,
#             feature_extractor=self.processor.feature_extractor,
#             max_new_tokens=128,
#             chunk_length_s=30,
#             batch_size=16,
#             return_timestamps=False,
#             torch_dtype=self.torch_dtype,
#             device=self.device,
#         )

#     def chat(self, prompt, audio_path):
#         """
#         参数与现有模型接口保持一致:
#         - prompt: 用户指令/问题
#         - audio_path: 音频文件路径
#         """
#         # 生成语音转录
#         transcript = " " + self.pipe(audio_path)["text"]
        
#         # 生成最终响应
#         try:
#             response = self.ltu_as.generate_with_raw_audio(
#                 audio_path=audio_path,
#                 instruction=prompt,
#                 transcript=transcript
#             )[0]
#             return response
#         except Exception as e:
#             print(f"LTU-AS推理错误: {str(e)}")
#             return ""

class BaichuanAudio:
    model_name = 'BaichuanAudio'

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.init_model()

    def init_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path, 
            device_map="cuda:0", 
            trust_remote_code=True, 
            torch_dtype=torch.bfloat16
        ).eval()

    def chat(self, prompt, audio_path):
        # 修改后的多模态输入构建方式
        inputs = [
            f'<audio>{audio_path}</audio>',
            prompt
        ]
        
        # 使用 tokenizer 的标准编码方式
        model_inputs = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": ''.join(inputs)}],
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)
        
        response = self.model.generate(
            inputs=model_inputs,
            max_new_tokens=4096,
            temperature=0.01,
            do_sample=False
        )
        
        return self.tokenizer.decode(response[0], skip_special_tokens=True)

# class MiniOmni2Audio:
#     model_name = 'MiniOmni2Audio'

#     def __init__(self, model_path=None):
#         self.model_path = model_path
#         self.init_model()

#     def init_model(self):
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
#         self.model = AutoModelForCausalLM.from_pretrained(
#             self.model_path, 
#             device_map="cuda:0",
#             trust_remote_code=True,
#             torch_dtype=torch.bfloat16
#         ).eval()

#     def chat(self, prompt, audio_path):
#         # 多模态输入构建：音频路径 + 文本提示
#         multimodal_input = [
#             f'<audio>{audio_path}</audio>',
#             prompt
#         ]
        
#         # 生成模型输入
#         model_inputs = self.tokenizer.apply_chat_template(
#             [{"role": "user", "content": "".join(multimodal_input)}],
#             add_generation_prompt=True,
#             return_tensors="pt"
#         ).to(self.model.device)
        
#         # 生成响应
#         response_ids = self.model.generate(
#             model_inputs,
#             max_new_tokens=1024,
#             temperature=0.01,
#             do_sample=False
#         )
        
#         return self.tokenizer.decode(response_ids[0], skip_special_tokens=True)



# class MiniOmni2Audio:
#     model_name = 'MiniOmni2Audio'

#     def __init__(self, model_path=None):
#         self.model_path = model_path
#         self.init_model()

#     def init_model(self):
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
#         self.model = AutoModelForCausalLM.from_pretrained(
#             self.model_path, 
#             device_map="cuda:0",
#             trust_remote_code=True,
#             torch_dtype=torch.bfloat16
#         ).eval()

#     def chat(self, prompt, audio_path):
#         # 多模态输入构建：音频路径 + 文本提示
#         multimodal_input = [
#             f'<audio>{audio_path}</audio>',
#             prompt
#         ]
        
#         # 生成模型输入
#         model_inputs = self.tokenizer.apply_chat_template(
#             [{"role": "user", "content": "".join(multimodal_input)}],
#             add_generation_prompt=True,
#             return_tensors="pt"
#         ).to(self.model.device)
        
#         # 生成响应
#         response_ids = self.model.generate(
#             model_inputs,
#             max_new_tokens=1024,
#             temperature=0.01,
#             do_sample=False
#         )
        
#         return self.tokenizer.decode(response_ids[0], skip_special_tokens=True)

# 在现有导入部分添加
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info
import soundfile as sf

# 在现有模型类后添加新类
class QwenOmniAudio:
    model_name = 'Qwen-Omni'
    
    def __init__(self, model_path=None, system='You are Qwen, a virtual human developed by the Qwen Team, Alibaba Group, capable of perceiving auditory and visual inputs, as well as generating text and speech.'):
        self.model_path = model_path
        self.system = system
        self.init_model()

    def init_model(self):
        # 优化1：强制使用bfloat16精度
        self.processor = Qwen2_5OmniProcessor.from_pretrained(self.model_path)
        self.model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,  # 强制使用bfloat16
            device_map="auto",
            attn_implementation="sdpa",  # 启用显存优化注意力
            low_cpu_mem_usage=True,
            max_memory={0: "30GiB"}  # 减少CPU内存占用
        ).eval()

    def chat(self, prompt, audio_path):
        # 优化2：分块处理长音频
        audio, sr = librosa.load(audio_path, sr=16000)
        chunk_size = 30 * sr  # 30秒分块
        chunks = [audio[i:i+chunk_size] for i in range(0, len(audio), chunk_size)]

        full_response = []
        # 添加索引来生成唯一文件名
        for idx, chunk in enumerate(chunks):
            # 使用索引代替哈希值
            tmp_path = f"tmp_{idx}.wav"  # 修改这里
            sf.write(tmp_path, chunk, sr)

            # 构建对话格式
            conversation = [
                {"role": "system", "content": [{"type": "text", "text": self.system}]},
                {"role": "user", "content": [
                    {"type": "audio", "audio": tmp_path},
                    {"type": "text", "text": prompt},
                ]},
            ]
            
            # 处理多模态输入
            text = self.processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
            audios, images, videos = process_mm_info(conversation, use_audio_in_video=False)
            
            # 优化3：使用内存优化参数
            with torch.inference_mode():
                inputs = self.processor(
                    text=text,
                    audio=audios,
                    return_tensors="pt",
                    padding=True
                ).to(self.model.device)

                # 优化4：启用分块生成
                # 修改生成参数
                text_ids, _ = self.model.generate(
                    **inputs,
                    max_new_tokens=512,  # 保留有效参数
                    temperature=0.01    # 保留有效参数
                    # 移除无效参数 chunk_size 和 use_cache_optimization
                )
                
                # 及时释放显存
                del inputs
                torch.cuda.empty_cache()

            response = self.processor.batch_decode(
                text_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            full_response.append(response)

        return " ".join(full_response)

# 在现有导入部分添加
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info
import soundfile as sf

# 在现有模型类后添加新类
class Qwen25OmniAudio:
    model_name = 'Qwen2.5-Omni'
    
    def __init__(self, model_path=None):
        self.model_path = model_path or "Qwen/Qwen2.5-Omni-3B"
        # Use default system prompt to avoid audio output issues
        self.system = 'You are Qwen, a virtual human developed by the Qwen Team, Alibaba Group, capable of perceiving auditory and visual inputs, as well as generating text and speech.'
        self.use_audio_in_video = False
        self.max_audio_length = 2000000  # Reduced from 3M to 2M (~125 seconds)
        self.max_new_tokens = 128  # Reduced from 256
        self.init_model()

    def init_model(self):
        # Set memory optimization environment variables
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
        os.environ['PYTORCH_NO_CUDA_MEMORY_CACHING'] = '1'
        
        self.processor = Qwen2_5OmniProcessor.from_pretrained(self.model_path)
        self.model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            attn_implementation="sdpa",  # More memory efficient
            low_cpu_mem_usage=True
        ).eval()

    def chat(self, prompt, audio_path, language='en'):
        conversation = [
            {
                "role": "system", 
                "content": [{"type": "text", "text": self.system}]
            },
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio": audio_path},
                    {"type": "text", "text": prompt},
                ],
            },
        ]
        
        text = self.processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        audios, images, videos = process_mm_info(conversation, use_audio_in_video=self.use_audio_in_video)
        
        inputs = self.processor(
            text=text,
            audio=audios,
            images=images,
            videos=videos,
            return_tensors="pt",
            padding=True,
            use_audio_in_video=self.use_audio_in_video
        ).to(self.model.device)

        with torch.inference_mode():
            # Check audio length first
            audio_input, _ = librosa.load(audio_path, sr=16000)
            if len(audio_input) > self.max_audio_length:
                print(f"Audio too long (> {self.max_audio_length} samples), skipping: {audio_path}")
                return ""

            # Clear cache before processing
            torch.cuda.empty_cache()
            
            text_ids, audio_output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=0.01,
                use_audio_in_video=self.use_audio_in_video
            )
            
        response = self.processor.batch_decode(
            text_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        # Save audio output
        sf.write(
            "output.wav",
            audio_output.reshape(-1).detach().cpu().numpy(),
            samplerate=24000,
        )
        
        return response

class MiniCPMAudio:
    model_name = 'MiniCPM-Audio'

    def __init__(self, model_path=None, system='You are a helpful assistant with audio understanding capabilities.'):
        self.model_path = model_path or 'OpenBMB/MiniCPM-o-2_6'
        self.system = system
        self.init_model()

    def init_model(self):
        try:
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                attn_implementation='sdpa',
                torch_dtype=torch.bfloat16,
                init_vision=False,
                init_audio=True,
                init_tts=True
            )
            self.model = self.model.eval().cuda()
            print("模型加载成功")
        except Exception as e:
            print(f"模型加载失败，错误信息: {e}")
            raise

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model.init_tts()
        self.model.tts.float()

    def chat(self, prompt, audio_path, language='en'):
        try:
            audio_input, _ = librosa.load(audio_path, sr=16000, mono=True)
            # 检查音频长度，如果超过 6000000 则直接返回空字符串
            if len(audio_input) > 6000000:
                print(f"音频长度超过 6000000，跳过处理: {audio_path}")
                return ""

            sys_msg = self.model.get_sys_prompt(mode='omni', language=language)
            msgs = [
                {"role": "system", "content": [{"type": "text", "text": sys_msg}]},
                {
                    "role": "user",
                    "content": [prompt, audio_input]
                }
            ]

            response = self.model.chat(
                msgs=msgs,
                tokenizer=self.tokenizer,
                sampling=True,
                temperature=0.5,
                max_new_tokens=4096,
                omni_input=True,
                use_tts_template=False,
                generate_audio=False,
                return_dict=True
            )
            return response.get('text', '')
        except torch.cuda.OutOfMemoryError:
            print(f"CUDA 内存不足，跳过处理: {audio_path}")
            torch.cuda.empty_cache()
            return ""
        except Exception as e:
            print(f"处理音频 {audio_path} 时出错: {e}")
            return ""

    def _load_audio(self, audio_path):
        try:
            audio, sr = librosa.load(audio_path, sr=16000)  # 可根据模型要求调整采样率
            return audio
        except Exception as e:
            print(f"Error loading audio file {audio_path}: {e}")
            return np.array([])

class GLM4Audio:
    model_name = 'glm-4-voice'

    def __init__(self, model_path):
        self.model_path = model_path
        self.init_model()

    def init_model(self):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, 
            trust_remote_code=True,
            # 添加模板配置
            chat_template="{% for message in messages %}{{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}{% endfor %}"
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path, 
            device_map="auto",
            trust_remote_code=True
        ).eval()

    def chat(self, prompt, audio_path):
        # 构建符合模板要求的输入格式
        messages = [
            {"role": "user", "content": f"[音频文件路径]: {audio_path}\n[用户指令]: {prompt}"}
        ]
        
        # 手动应用模板
        input_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_new_tokens=1024,
            temperature=0.01
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

class BaichuanOmniAudio:
    model_name = 'BaichuanOmniAudio'
    
    def __init__(self, model_path=None, system='You are a helpful Assistant.'):
        self.model_path = model_path
        self.system = system
        self.init_model()

    def init_model(self):
        # 添加缺失的flash_attn依赖
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, 
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",  # This requires accelerate
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        ).eval()

    def chat(self, prompt, audio_path):
        # 使用适配Omni模型的对话格式
        conversation = [{
            'role': 'user',
            'content': f'<audio>{audio_path}</audio>{prompt}'  # 将音频路径作为特殊标记嵌入
        }]
        
        # 添加生成配置
        input_ids = self.tokenizer.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            return_tensors="pt",
            tokenize=True
        ).to(self.model.device)
        
        outputs = self.model.generate(
            input_ids,
            max_new_tokens=1024,
            temperature=0.01,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # 更安全的解码方式
        response = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        ).split('<|assistant|>')[-1].strip()
        
        return response
