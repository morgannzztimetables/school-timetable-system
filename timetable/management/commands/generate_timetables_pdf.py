import os
from django.core.management.base import BaseCommand
from timetable.models import SchoolClass, Teacher, TimeSlot, TimetableEntry
from fpdf import FPDF

SCHOOL_NAME = "MISEMWA FRIENDS SENIOR SCHOOL"

class Command(BaseCommand):
    help = "Generate class and teacher timetable PDFs"

    def handle(self, *args, **kwargs):
        pdf_folder = os.path.join(os.getcwd(), "timetables_pdfs")
        os.makedirs(pdf_folder, exist_ok=True)

        self.stdout.write("Generating timetables...")

        for school_class in SchoolClass.objects.all():
            self.generate_class_pdf(school_class, pdf_folder)

        for teacher in Teacher.objects.all():
            self.generate_teacher_pdf(teacher, pdf_folder)

        self.stdout.write(self.style.SUCCESS("All timetable PDFs generated successfully."))

    def generate_class_pdf(self, class_obj, folder):
        pdf = FPDF(orientation="L")  # Landscape
        pdf.add_page()

        # Header
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, SCHOOL_NAME, ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Class Timetable - {class_obj.name}", ln=True, align="C")
        pdf.ln(4)

        # Column/row settings
        max_width = pdf.w - 20  # leave margin
        col_width = 20  # fixed
        # Get timeslots
        timeslots = TimeSlot.objects.order_by("start_time")
        seen = set()
        unique_timeslots = []
        for slot in timeslots:
            if slot.start_time not in seen:
                unique_timeslots.append(slot)
                seen.add(slot.start_time)

        days = ["MON", "TUE", "WED", "THU", "FRI"]
        num_rows = len(days) + 1  # including header
        num_cols = len(unique_timeslots) + 1  # including day column

        # Calculate max row height to fit page
        available_height = pdf.h - 40  # leave header margin
        row_height = min(30, available_height / num_rows)

        # Reduce font size if table is too wide
        total_table_width = col_width * num_cols
        font_size = 9
        if total_table_width > max_width:
            col_width = max_width / num_cols
            font_size = 8

        pdf.set_font("Arial", "", font_size)

        # Header row
        pdf.cell(col_width, row_height, "DAY", border=1, align="C")
        for slot in unique_timeslots:
            x, y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(col_width, row_height / 2, f"{slot.start_time}\n{slot.end_time}", border=1, align="C")
            pdf.set_xy(x + col_width, y)
        pdf.ln(row_height)

        # Table body
        for day in days:
            pdf.cell(col_width, row_height, day, border=1, align="C")
            for slot in unique_timeslots:
                entries = TimetableEntry.objects.filter(
                    school_class=class_obj,
                    timeslot__day=day,
                    timeslot__start_time=slot.start_time
                )
                x, y = pdf.get_x(), pdf.get_y()
                if entries.exists():
                    lines = []
                    for entry in entries:
                        initials = entry.teacher.initials if entry.teacher else "N/A"
                        lines.append(f"{entry.subject.name} ({initials})")
                    pdf.multi_cell(col_width, row_height / 2, "\n".join(lines), border=1, align="C")
                else:
                    pdf.multi_cell(col_width, row_height, "", border=1, align="C")
                pdf.set_xy(x + col_width, y)
            pdf.ln(row_height)

        pdf.output(os.path.join(folder, f"class_{class_obj.name}.pdf"))

    # Teacher timetable remains unchanged
    def generate_teacher_pdf(self, teacher_obj, folder):
        pdf = FPDF(orientation="L")
        pdf.add_page()

        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 12, SCHOOL_NAME, ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Teacher Timetable - {teacher_obj.first_name} {teacher_obj.last_name}", ln=True, align="C")
        pdf.ln(6)

        row_height = 25
        col_width = 20

        timeslots = TimeSlot.objects.order_by("start_time")
        seen = set()
        unique_timeslots = []
        for slot in timeslots:
            if slot.start_time not in seen:
                unique_timeslots.append(slot)
                seen.add(slot.start_time)

        days = ["MON", "TUE", "WED", "THU", "FRI"]

        pdf.set_font("Arial", "B", 11)
        pdf.cell(col_width, row_height, "DAY", border=1, align="C")
        for slot in unique_timeslots:
            x, y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(col_width, row_height / 2, f"{slot.start_time}\n{slot.end_time}", border=1, align="C")
            pdf.set_xy(x + col_width, y)
        pdf.ln(row_height)

        pdf.set_font("Arial", "", 11)
        for day in days:
            pdf.cell(col_width, row_height, day, border=1, align="C")
            for slot in unique_timeslots:
                entries = TimetableEntry.objects.filter(
                    teacher=teacher_obj,
                    timeslot__day=day,
                    timeslot__start_time=slot.start_time
                )
                x, y = pdf.get_x(), pdf.get_y()
                if entries.exists():
                    lines = []
                    for entry in entries:
                        lines.append(f"{entry.subject.name} ({entry.school_class.name})")
                    pdf.multi_cell(col_width, row_height / 2, "\n".join(lines), border=1, align="C")
                else:
                    pdf.multi_cell(col_width, row_height, "", border=1, align="C")
                pdf.set_xy(x + col_width, y)
            pdf.ln(row_height)

        pdf.output(os.path.join(folder, f"teacher_{teacher_obj.first_name}_{teacher_obj.last_name}.pdf"))
