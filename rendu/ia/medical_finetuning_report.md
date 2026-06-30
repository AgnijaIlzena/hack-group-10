
# Medical Fine-Tuning Report

## Objective
Fine-tune an experimental medical chatbot using LoRA.

## Base Model
Qwen/Qwen2.5-0.5B-Instruct

## Dataset
ruslanmv/ai-medical-chatbot

## Method
QLoRA 4-bit + LoRA adapter.

## Training Configuration
- max_steps: 100
- batch_size: 1
- gradient_accumulation_steps: 4
- learning_rate: 5e-5
- max_length: 512
- LoRA rank: 8
- LoRA alpha: 16

## Final Training Logs
[{'loss': 2.3116674423217773, 'grad_norm': 1.2142621278762817, 'learning_rate': 8.947368421052632e-06, 'epoch': 0.001393042979473102, 'step': 85}, {'loss': 2.341084289550781, 'grad_norm': 1.1897650957107544, 'learning_rate': 6.315789473684211e-06, 'epoch': 0.0014749866841479904, 'step': 90}, {'loss': 2.3878129959106444, 'grad_norm': 1.0191001892089844, 'learning_rate': 3.6842105263157892e-06, 'epoch': 0.0015569303888228786, 'step': 95}, {'loss': 2.436814880371094, 'grad_norm': 1.246286392211914, 'learning_rate': 1.0526315789473685e-06, 'epoch': 0.001638874093497767, 'step': 100}, {'train_runtime': 195.1018, 'train_samples_per_second': 2.05, 'train_steps_per_second': 0.513, 'total_flos': 445190819020800.0, 'train_loss': 2.5523900604248047, 'epoch': 0.001638874093497767, 'step': 100}]

## Safety
This model is experimental only.
It must not be used for clinical diagnosis, prescriptions, emergency decisions, or replacing a healthcare professional.

## Deliverable
techcorp-medical-lora.zip
