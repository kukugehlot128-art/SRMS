from core.models import Timetable

Timetable.objects.all().delete()
print("All Timetable data removed successfully!")
