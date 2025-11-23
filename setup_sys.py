# import torch
# print("PyTorch Version:", torch.__version__)
# print("CUDA Available:", torch.cuda.is_available())
# print("GPU Name:", torch.cuda.get_device_name(0))

import torch
import time

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using Device:", device)

# Test 1: Simple matrix multiplication
x = torch.rand(10000, 10000).to(device)

start = time.time()
y = torch.matmul(x, x)
end = time.time()

print("Time taken:", end - start)
