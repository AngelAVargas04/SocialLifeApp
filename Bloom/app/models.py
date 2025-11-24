from django.db import models

# Create your models here.
class posts(models.Model):
    subject = models.CharField(max_length=100)
    # subject of the post
    description = models.TextField()
    # body of post
    slug = models.SlugField()
    # slug is for unique URLs
    date_posted = models.DateTimeField(auto_now_add=True)
    # date the post was created.

    def __str__(self):
        return self.subject