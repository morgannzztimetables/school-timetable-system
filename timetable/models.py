from django.db import models
class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SchoolClass(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    classes = models.ManyToManyField(SchoolClass)

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.day} {self.start_time}-{self.end_time}"

class TimetableEntry(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True,)

    def __str__(self):
        if self.subject.teacher:
            return f"{self.school_class} - {self.subject.teacher.initials} - {self.timeslot}"
        return f"{self.school_class} - {self.subject} - {self.timeslot}"
