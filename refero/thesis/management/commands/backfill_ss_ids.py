from django.core.management.base import BaseCommand
from thesis.models import Thesis
from thesis.views import get_paper_id
import time

class Command(BaseCommand):
    help = 'Backfills Semantic Scholar Paper IDs for existing theses'

    def handle(self, *args, **options):
        theses_without_id = Thesis.objects.filter(ss_paper_id__isnull=True) | Thesis.objects.filter(ss_paper_id='')
        total = theses_without_id.count()
        
        self.stdout.write(f"Found {total} theses without Semantic Scholar IDs.")

        for i, thesis in enumerate(theses_without_id, 1):
            self.stdout.write(f"Processing ({i}/{total}): {thesis.title}")
            
            ss_id = get_paper_id(thesis.title)
            
            if ss_id:
                thesis.ss_paper_id = ss_id
                thesis.save()
                self.stdout.write(self.style.SUCCESS(f"  -> Found ID: {ss_id}"))
            else:
                self.stdout.write(self.style.WARNING(f"  -> No ID found for '{thesis.title}'"))
            
            # Sleep briefly to avoid hitting API rate limits too hard
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Backfill process completed.'))
