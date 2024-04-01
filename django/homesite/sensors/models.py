from django.db import models



class SensorReading(models.Model):

    param = models.CharField(max_length=10, default='unk')
    date = models.DateTimeField("datetime")
    reading = models.FloatField("reading")

    def __str__(self):
        return f'{self.date} : {self.param} : {self.reading}'
    