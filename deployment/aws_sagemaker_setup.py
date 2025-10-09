#!/usr/bin/env python3
"""
AWS SageMaker Fine-Tuning Setup for Dependency-Specialized LLM
Creates the infrastructure and training job for Libraries.io fine-tuning
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, List

class DependencyLLMTrainer:
    """Setup and manage AWS SageMaker training for dependency-specialized LLM"""

    def __init__(self, region='us-west-2'):
        self.region = region
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.iam = boto3.client('iam', region_name=region)

    def create_training_job_config(self,
                                 model_name: str = "dependency-llm-v1",
                                 base_model: str = "codellama-7b",
                                 instance_type: str = "ml.g5.12xlarge") -> Dict:
        """Create SageMaker training job configuration"""

        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        job_name = f"{model_name}-{timestamp}"

        training_config = {
            "TrainingJobName": job_name,
            "AlgorithmSpecification": {
                "TrainingImage": "763104351884.dkr.ecr.us-west-2.amazonaws.com/huggingface-pytorch-training:2.0.1-transformers4.31.0-gpu-py310-cu118-ubuntu20.04",
                "TrainingInputMode": "File",
                "EnableSageMakerMetricsTimeSeries": True
            },
            "RoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/SageMakerExecutionRole",  # Replace with your role
            "InputDataConfig": [
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": f"s3://your-dependency-data-bucket/training/",  # Replace with your bucket
                            "S3DataDistributionType": "FullyReplicated"
                        }
                    },
                    "ContentType": "application/json",
                    "CompressionType": "None"
                },
                {
                    "ChannelName": "validation",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": f"s3://your-dependency-data-bucket/validation/",
                            "S3DataDistributionType": "FullyReplicated"
                        }
                    },
                    "ContentType": "application/json",
                    "CompressionType": "None"
                }
            ],
            "OutputDataConfig": {
                "S3OutputPath": f"s3://your-dependency-data-bucket/models/{job_name}/"
            },
            "ResourceConfig": {
                "InstanceType": instance_type,
                "InstanceCount": 1,
                "VolumeSizeInGB": 500
            },
            "StoppingCondition": {
                "MaxRuntimeInSeconds": 86400  # 24 hours max
            },
            "HyperParameters": {
                "model_name": base_model,
                "learning_rate": "2e-5",
                "batch_size": "4",
                "num_epochs": "3",
                "max_seq_length": "2048",
                "lora_r": "64",
                "lora_alpha": "128",
                "lora_dropout": "0.1",
                "gradient_checkpointing": "true",
                "fp16": "true",
                "save_steps": "500",
                "eval_steps": "500",
                "logging_steps": "100",
                "warmup_steps": "100"
            },
            "Tags": [
                {"Key": "Project", "Value": "DependencyLLM"},
                {"Key": "Environment", "Value": "Training"},
                {"Key": "CostCenter", "Value": "Research"}
            ]
        }

        return training_config

    def create_training_script(self) -> str:
        """Create the training script for dependency LLM fine-tuning"""

        script = '''
import os
import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset, load_dataset
from peft import LoraConfig, get_peft_model, TaskType
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="codellama/CodeLlama-7b-Python-hf")
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--num_epochs", type=int, default=3)
    parser.add_argument("--max_seq_length", type=int, default=2048)
    parser.add_argument("--lora_r", type=int, default=64)
    parser.add_argument("--lora_alpha", type=int, default=128)
    parser.add_argument("--lora_dropout", type=float, default=0.1)
    return parser.parse_args()

def format_dependency_prompt(example):
    """Format training examples for dependency prediction"""
    instruction = "Analyze the dependencies for this Python code and predict execution success."

    input_text = f"""### Instruction:
{instruction}

### Input:
```python
{example['code']}
```

### Response:
{json.dumps(example['output'], indent=2)}"""

    return input_text

def load_and_prepare_data(data_path):
    """Load and prepare dependency training data"""
    # Load your prepared dependency dataset
    dataset = load_dataset('json', data_files=f"{data_path}/*.json")

    # Format for instruction following
    def format_examples(examples):
        formatted = []
        for i in range(len(examples['code'])):
            formatted_text = format_dependency_prompt({
                'code': examples['code'][i],
                'output': examples['output'][i]
            })
            formatted.append(formatted_text)
        return {'text': formatted}

    dataset = dataset.map(format_examples, batched=True)
    return dataset

def main():
    args = parse_args()

    # Setup model and tokenizer
    model_name = args.model_name
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )

    # Setup LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and prepare data
    train_data = load_and_prepare_data("/opt/ml/input/data/training")
    val_data = load_and_prepare_data("/opt/ml/input/data/validation")

    # Tokenize data
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=args.max_seq_length
        )

    train_dataset = train_data.map(tokenize_function, batched=True)
    val_dataset = val_data.map(tokenize_function, batched=True)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="/opt/ml/model",
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        warmup_steps=100,
        logging_steps=100,
        eval_steps=500,
        save_steps=500,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,
        gradient_checkpointing=True,
        dataloader_pin_memory=False,
        report_to=None
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # Train the model
    trainer.train()

    # Save the final model
    trainer.save_model("/opt/ml/model")
    tokenizer.save_pretrained("/opt/ml/model")

if __name__ == "__main__":
    main()
'''
        return script

    def create_requirements_txt(self) -> str:
        """Create requirements.txt for training environment"""
        requirements = '''
torch>=2.0.1
transformers>=4.31.0
datasets>=2.14.0
peft>=0.4.0
accelerate>=0.21.0
bitsandbytes>=0.41.0
scipy
numpy
pandas
tqdm
'''
        return requirements

    def setup_s3_bucket(self, bucket_name: str):
        """Create S3 bucket and folder structure"""
        try:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            print(f"✓ Created S3 bucket: {bucket_name}")
        except Exception as e:
            print(f"Bucket might already exist: {e}")

        # Create folder structure
        folders = [
            'training/',
            'validation/',
            'models/',
            'scripts/',
            'data/libraries_io/',
            'data/sciunit/'
        ]

        for folder in folders:
            self.s3.put_object(
                Bucket=bucket_name,
                Key=folder,
                Body=''
            )

        print("✓ Created S3 folder structure")

    def create_cost_estimate(self,
                           instance_type: str = "ml.g5.12xlarge",
                           training_hours: int = 8) -> Dict:
        """Estimate training costs"""

        # AWS pricing (approximate, varies by region)
        instance_costs = {
            "ml.g5.12xlarge": {"on_demand": 7.09, "spot": 2.13},
            "ml.g5.24xlarge": {"on_demand": 14.18, "spot": 4.25},
            "ml.p4d.24xlarge": {"on_demand": 32.77, "spot": 9.83}
        }

        storage_cost = 0.10 * 500 / 30  # $0.10/GB/month, 500GB, daily usage

        on_demand_compute = instance_costs[instance_type]["on_demand"] * training_hours
        spot_compute = instance_costs[instance_type]["spot"] * training_hours

        estimate = {
            "instance_type": instance_type,
            "training_hours": training_hours,
            "costs": {
                "on_demand_total": on_demand_compute + storage_cost,
                "spot_total": spot_compute + storage_cost,
                "savings_with_spot": on_demand_compute - spot_compute,
                "storage_daily": storage_cost
            },
            "recommendations": [
                "Use spot instances for 70% cost savings",
                "Consider ml.g5.12xlarge for good price/performance",
                "Stop instance immediately after training",
                "Use gradient checkpointing to reduce memory"
            ]
        }

        return estimate

    def generate_setup_commands(self) -> List[str]:
        """Generate AWS CLI commands for quick setup"""

        commands = [
            "# 1. Create S3 bucket for training data",
            "aws s3 mb s3://your-dependency-llm-bucket",
            "",
            "# 2. Upload training scripts",
            "aws s3 cp train.py s3://your-dependency-llm-bucket/scripts/",
            "aws s3 cp requirements.txt s3://your-dependency-llm-bucket/scripts/",
            "",
            "# 3. Create IAM role (if not exists)",
            "aws iam create-role --role-name SageMakerDependencyLLM --assume-role-policy-document file://trust-policy.json",
            "aws iam attach-role-policy --role-name SageMakerDependencyLLM --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
            "",
            "# 4. Start training job",
            "python aws_sagemaker_setup.py --start-training",
            "",
            "# 5. Monitor training",
            "aws sagemaker describe-training-job --training-job-name dependency-llm-v1-TIMESTAMP"
        ]

        return commands

def main():
    """Main execution function"""
    trainer = DependencyLLMTrainer()

    print("🚀 AWS SageMaker Dependency LLM Setup")
    print("=" * 50)

    # Generate training configuration
    config = trainer.create_training_job_config()
    print("✓ Generated training job configuration")

    # Create training script
    script = trainer.create_training_script()
    with open('train.py', 'w') as f:
        f.write(script)
    print("✓ Created training script")

    # Create requirements
    requirements = trainer.create_requirements_txt()
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✓ Created requirements.txt")

    # Generate cost estimate
    cost_estimate = trainer.create_cost_estimate()
    print("\n💰 Cost Estimate:")
    print(f"   Instance: {cost_estimate['instance_type']}")
    print(f"   Training Hours: {cost_estimate['training_hours']}")
    print(f"   On-Demand Cost: ${cost_estimate['costs']['on_demand_total']:.2f}")
    print(f"   Spot Instance Cost: ${cost_estimate['costs']['spot_total']:.2f}")
    print(f"   Savings with Spot: ${cost_estimate['costs']['savings_with_spot']:.2f}")

    # Save configuration
    with open('sagemaker_config.json', 'w') as f:
        json.dump(config, f, indent=2, default=str)

    print("\n📋 Setup Commands:")
    commands = trainer.generate_setup_commands()
    for cmd in commands:
        print(cmd)

    print("\n🎯 Next Steps:")
    print("1. Prepare Libraries.io training data")
    print("2. Upload data to S3 bucket")
    print("3. Update IAM role ARN in config")
    print("4. Start SageMaker training job")
    print("5. Monitor training progress")

    print("\n✅ AWS SageMaker setup complete!")

if __name__ == "__main__":
    main()