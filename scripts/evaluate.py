#!/usr/bin/env python3
"""
Evaluation script for testing the chatbot.
This script is complete - students should NOT modify.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chat_engine import get_engine
from src.config import OUTPUTS_FILE, SCHEMA_FILE, TESTS_DIR
from src.io_utils import (
    load_schema,
    read_jsonl,
    validate_record,
    write_jsonl,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def evaluate_single(engine, test_case: Dict) -> Dict:
    """
    Evaluate a single test case.
    
    Args:
        engine: Chat engine instance
        test_case: Test input with 'id' and 'prompt' fields
        
    Returns:
        Evaluation result dictionary
    """
    test_id = test_case.get("id", "unknown")
    prompt = test_case.get("prompt", "")
    
    logger.info(f"Evaluating test {test_id}")
    
    try:
        # Reset engine for clean state
        engine.reset()
        
        # Process the message
        result = engine.process_message(prompt, include_context=False)
        
        # Format output according to schema
        output = {
            "id": test_id,
            "prompt": prompt,
            "response": result.get("response", ""),
            "safety_action": result.get("safety_action", "allow"),
            "policy_tags": result.get("policy_tags", []),
            "latency_ms": result.get("latency_ms", 0),
            "model_name": result.get("model_name", "unknown"),
            "deterministic": result.get("deterministic", True),
        }
        
        return output
        
    except Exception as e:
        logger.error(f"Failed to evaluate test {test_id}: {e}")
        return {
            "id": test_id,
            "prompt": prompt,
            "response": f"ERROR: {str(e)}",
            "safety_action": "error",
            "policy_tags": ["error"],
            "latency_ms": 0,
            "model_name": "unknown",
            "deterministic": False,
        }


def run_evaluation(
    input_file: str,
    output_file: str,
    schema_file: str,
) -> int:
    """
    Run evaluation on all test cases.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file
        schema_file: Path to schema JSON file
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    logger.info("Starting evaluation")
    
    # Load test cases
    try:
        test_cases = read_jsonl(input_file)
        logger.info(f"Loaded {len(test_cases)} test cases")
    except Exception as e:
        logger.error(f"Failed to load test cases: {e}")
        return 1
    
    # Load schema
    try:
        schema = load_schema(schema_file)
        logger.info("Loaded output schema")
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        return 1
    
    # Initialize engine
    try:
        engine = get_engine()
        logger.info("Initialized chat engine")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        return 1
    
    # Evaluate all test cases
    outputs = []
    failed_validations = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Processing test {i}/{len(test_cases)}")
        
        # Evaluate
        output = evaluate_single(engine, test_case)
        outputs.append(output)
        
        # Validate against schema
        if not validate_record(output, schema):
            failed_validations.append(output["id"])
            logger.warning(f"Test {output['id']} failed schema validation")
        
        # Brief delay to avoid overwhelming the model
        if i < len(test_cases):
            time.sleep(0.1)
    
    # Write outputs
    try:
        write_jsonl(outputs, output_file)
        logger.info(f"Wrote outputs to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write outputs: {e}")
        return 1
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Total tests: {len(test_cases)}")
    print(f"Completed: {len(outputs)}")
    print(f"Schema violations: {len(failed_validations)}")
    
    # Count safety actions
    safety_counts = {}
    for output in outputs:
        action = output.get("safety_action", "unknown")
        safety_counts[action] = safety_counts.get(action, 0) + 1
    
    print("\nSafety Actions:")
    for action, count in safety_counts.items():
        print(f"  {action}: {count}")
    
    # Calculate statistics
    latencies = [o.get("latency_ms", 0) for o in outputs if o.get("latency_ms")]
    if latencies:
        print(f"\nLatency Statistics:")
        print(f"  Min: {min(latencies)}ms")
        print(f"  Max: {max(latencies)}ms")
        print(f"  Avg: {sum(latencies)/len(latencies):.1f}ms")
    
    print("="*60)
    
    # Determine exit code
    if failed_validations:
        print(f"\nFAILED: {len(failed_validations)} schema violations")
        print(f"Failed IDs: {', '.join(failed_validations)}")
        return 1
    
    if len(outputs) < len(test_cases):
        print(f"\nFAILED: Only {len(outputs)}/{len(test_cases)} tests completed")
        return 1
    
    print("\nPASSED: All tests completed successfully")
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate the chatbot on test cases"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=os.path.join(TESTS_DIR, "inputs.jsonl"),
        help="Input test file (JSONL)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=OUTPUTS_FILE,
        help="Output results file (JSONL)"
    )
    parser.add_argument(
        "--schema",
        type=str,
        default=SCHEMA_FILE,
        help="Output schema file (JSON)"
    )
    
    args = parser.parse_args()
    
    # Run evaluation
    exit_code = run_evaluation(
        input_file=args.input,
        output_file=args.output,
        schema_file=args.schema,
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()