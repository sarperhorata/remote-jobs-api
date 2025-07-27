import asyncio
import logging

from distill_crawler import DistillCrawler

logging.basicConfig(level=logging.INFO)


async def main():
    crawler = DistillCrawler()
    crawler.load_companies_data()
    jobs = await crawler.crawl_all_companies()
    result = crawler.save_jobs_to_database(jobs)
    print(f"Crawling completed: {result}")


if __name__ == "__main__":
    asyncio.run(main())
