from django.db import models

# Create your models here.

class NaatVideo(models.Model):
    title = models.CharField(max_length=255)
    video_link = models.URLField()
    tags = models.TextField(default="", blank=True, null=True, help_text="Comma-separated tags")  # Store tags as comma-separated values

    def get_tags(self):
        """ Return tags as a list """
        return [tag.strip().lower() for tag in self.tags.split(",") if tag.strip()]
    
    def __str__(self):
        return self.title
