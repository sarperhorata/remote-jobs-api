import logging
import os
import re

from pymongo import MongoClient

logger = logging.getLogger(__name__)


def fix_linkedin_companies():
    # Use synchronous client
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    db = client["buzz2remote"]

    # First, find all jobs with the problematic company name
    problematic_pattern = "Linkedin icon linkedintwitter-greytwitterinstagraminstagrampodcast-greypodcastLinkedin icon linked"

    # Find all jobs with this problematic company name
    cursor = db.jobs.find({"company": {"$regex": problematic_pattern, "$options": "i"}})
    jobs = list(cursor)

    print(f"Found {len(jobs)} jobs with problematic company names")

    if not jobs:
        print("No problematic companies found!")
        client.close()
        return

    # Try to extract real company names from other fields or use a default
    updated_count = 0

    for job in jobs:
        job_id = job["_id"]
        current_company = job.get("company", "")

        # Try to find a real company name from the job title or other fields
        title = job.get("title", "")
        description = job.get("description", "")
        url = job.get("url", "")

        # Extract potential company name from URL domain
        new_company_name = "Unknown Company"

        if url:
            try:
                # Extract domain from URL
                domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
                if domain_match:
                    domain = domain_match.group(1)
                    # Clean up domain to get company name
                    domain_parts = domain.split(".")
                    if len(domain_parts) >= 2:
                        potential_name = domain_parts[0]
                        # Capitalize and clean
                        new_company_name = potential_name.replace("-", " ").title()

                        # Some common mappings
                        if "linkedin" in potential_name.lower():
                            new_company_name = "LinkedIn"
                        elif "remote" in potential_name.lower():
                            new_company_name = "Remote Company"
                        elif "github" in potential_name.lower():
                            new_company_name = "GitHub"
                        elif len(potential_name) < 3:
                            new_company_name = "Tech Company"
            except Exception as e:
                logger.debug(f"Error processing company: {e}")
                pass

        # Update the job with the new company name
        result = db.jobs.update_one(
            {"_id": job_id}, {"$set": {"company": new_company_name}}
        )

        if result.modified_count > 0:
            updated_count += 1
            if updated_count <= 5:  # Show first 5 examples
                print(
                    f"Updated job {job_id}: '{current_company[:50]}...' -> '{new_company_name}'"
                )

    print(f"\nSuccessfully updated {updated_count} jobs")

    # Also fix any other problematic entries
    other_problematic = db.jobs.find(
        {
            "company": {
                "$regex": "linkedintwitter|instagrampodcast|icon.*icon",
                "$options": "i",
            }
        }
    )
    other_count = 0

    for job in other_problematic:
        result = db.jobs.update_one(
            {"_id": job["_id"]}, {"$set": {"company": "Tech Company"}}
        )
        if result.modified_count > 0:
            other_count += 1

    if other_count > 0:
        print(f"Fixed {other_count} additional problematic entries")

    client.close()
    print("Company name cleanup completed!")


if __name__ == "__main__":
    fix_linkedin_companies()
