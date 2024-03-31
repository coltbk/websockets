from django.core.management.base import BaseCommand, CommandError
from sensors.models import SensorReading
import serial
from django.utils import timezone


class Command(BaseCommand):
    help = "starts data collection"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
            ser = serial.Serial('COM4', 9600, timeout=1) #windows
            ser.reset_input_buffer()

            while True:
            # for i in range(10):
                current_datetime = timezone.now()#.strftime("%Y-%m-%d %H:%M:%S")

                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    split_line = line.split(',')
                    temp = split_line[0]
                    distance = split_line[1]
                    self.stdout.write(str(current_datetime) + ': ' + line)
                    self.stdout.write('\n')
                    reading = SensorReading(param='temp', date=current_datetime, reading=temp)
                    reading.save()
                # i += 1

            # self.stdout.write(
            #     self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
            # )

