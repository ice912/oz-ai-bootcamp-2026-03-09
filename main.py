#print("Hello worker")
import json
import redis
from llama_cpp import Llama

redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

def create_response(question: str):
    # SYSYEM_PROMPT 등 필요한 변수가 사전에 정의되어 있어야 합니다.
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}, # "role" 오타 수정 및 SYSTEM_PROMPT 변수명 확인
            {"role": "user", "content": question}
        ],
        max_tokens = 256,
        temperature = 0.7,
    )
    return response["choices"][0]["message"]["content"]

def run():
        #[1] Job을 deque
    while True:
        _, job_data = redis_client.brpop("inference_queue")
        job = json.loads(job_data)

    #[2] 추론
    answer = create_response(question=job["question"])
        #question = job["question"]
    channel = f"result:{job["id"]}"
    redis_client.publish(channel, answer)

if __name__ == "__main__":
    run()