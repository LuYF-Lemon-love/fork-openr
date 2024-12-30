from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
import torch

good_token = '+'
bad_token = '-'
step_tag = 'ки'

tokenizer = AutoTokenizer.from_pretrained('peiyi9979/math-shepherd-mistral-7b-prm')

candidate_tokens = tokenizer.encode(f"{good_token} {bad_token}")[1:] # [648, 387]
print(tokenizer.encode(f"{good_token}")) # [1, 648]
print(tokenizer.encode(f"{bad_token}")) # [1, 387]
print(f"candidate_tokens: {candidate_tokens}\n") # [648, 387]

step_tag_id = tokenizer.encode(f"{step_tag}")[-1] # 12902
print(tokenizer.encode(f"{step_tag}")) # [1, 12902]
print(f"step_tag_id: {step_tag_id}\n") # 12902

model = AutoModelForCausalLM.from_pretrained('peiyi9979/math-shepherd-mistral-7b-prm').eval()

question = """Janet\u2019s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?"""
output1 = """Step 1: Janet's ducks lay 16 eggs per day. ки\nStep 2: She eats three for breakfast every morning, so she has 16 - 3 = 13 eggs left. ки\nStep 3: She bakes muffins for her friends every day with four eggs, so she has 13 - 4 = 9 eggs left. ки\nStep 4: She sells the remainder at the farmers' market daily for $2 per fresh duck egg, so she makes 9 * $2 = $18 every day at the farmers' market. The answer is: 18 ки""" # 18 is right
output2 = """Step 1: Janet's ducks lay 16 eggs per day. ки\nStep 2: She eats three for breakfast every morning, so she has 16 - 3 = 13 eggs left. ки\nStep 3: She bakes muffins for her friends every day with four eggs, so she has 13 - 4 = 9 eggs left. ки\nStep 4: She sells the remainder at the farmers' market daily for $2 per fresh duck egg, so she makes 9 * $2 = $17 every day at the farmers' market. The answer is: 17 ки""" # 17 is wrong

for output in [output1, output2]:
    input_for_prm = f"{question} {output}"
    input_id = torch.tensor([tokenizer.encode(input_for_prm)])
    print(f"\ninput_id.shape: {input_id.shape}")

    with torch.no_grad():
        logits = model(input_id).logits
        print(f"logits.shape: {logits.shape}")
        logits = logits[:,:,candidate_tokens]
        print(f"logits.shape: {logits.shape}")
        scores = logits.softmax(dim=-1)[:,:,0] 
        print(f"scores.shape: {scores.shape}")
        print(f"input_id.shape: {input_id.shape}")
        print(f"step_tag_id: {step_tag_id}")
        step_scores = scores[input_id == step_tag_id]
        print(step_scores)
        
# tensor([0.9955, 0.9958, 0.9983, 0.9957])
# tensor([0.9955, 0.9958, 0.9983, 0.0240])