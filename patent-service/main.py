import os
import sys
import argparse

from src.service.pipeline import PatentAdvisorPipeLine
from src.utils import logger
import src.utils as utils
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def main():

    parser = argparse.ArgumentParser(description="My script that accepts arguments")

    # Add arguments
    parser.add_argument('--job', type=str, help="Name of job (upload/trigger_pipeline")
    parser.add_argument('--upload_path', type=str, help="Path to upload pdf files")
    parser.add_argument('--type', type=str, help="Type of pipeline job", default="all")

    # Parse the arguments
    args = parser.parse_args()

    # Use the arguments
    logger.info(f"Pipeline is invoked with {args.job}")
    pipeline = PatentAdvisorPipeLine()
    if args.job == "upload":
        dir_path = args.upload_path
        logger.info(f"User triggering pdf upload from directory {dir_path}")
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        for f in files:
            pipeline.upload_file(os.path.join(dir_path, f))
    elif args.job == "trigger_pipeline":
        pipeline.trigger_pipeline(args.type)
    else:
        logger.info(f"Invalid job passed {args}")


if __name__ == "__main__":
    main()


#python3 -m main --job upload --upload_path /Users/amitarora/workspace/poc-workspace/capstone/patentadvisor/patent-service/dataset/documents/test_dir
#python3 -m main --job trigger_pipeline --type all