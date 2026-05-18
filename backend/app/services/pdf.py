"""PDF export of summary reports.
Builds an  PDF report using reportlab """

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from app.models import User

# Colour palette
BLACK = colors.HexColor("#0a0f1c")
GREY  = colors.HexColor("#6b7280")
GREEN = colors.HexColor("#059669")
RED   = colors.HexColor("#dc2626")


class PdfService:
    """Builds an A4 PDF summary for a user"""

    def build_summary(
        self, user: User, transactions: list,
        date_from: str = "", date_to: str = "",
    ) -> bytes:
        """Return the PDF as bytes"""
        rows = sorted(transactions, key=lambda t: t.date)
        income  = sum(t.amount for t in rows if t.type == "income")
        expense = sum(t.amount for t in rows if t.type == "expense")

        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4, title="FinTrack Summary",
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=18 * mm, bottomMargin=18 * mm,
        )

        story = []
        story += self._header(user, date_from, date_to)
        story += [Spacer(1, 8 * mm), self._stat_band(income, expense, len(rows))]
        story += [Spacer(1, 10 * mm), Paragraph("Transactions", self._h2()),
                  Spacer(1, 4 * mm), self._transactions_table(rows)]
        story += [Spacer(1, 10 * mm), Paragraph("Expenses by Category", self._h2()),
                  Spacer(1, 4 * mm), self._category_table(rows)]
        story += [Spacer(1, 10 * mm), Paragraph("By Payment Method", self._h2()),
                  Spacer(1, 4 * mm), self._method_table(rows)]

        doc.build(story)
        return buf.getvalue()

    # Sections

    def _header(self, user: User, date_from: str, date_to: str):
        """Title and name on the left, FROM/TO dates on the right"""
        title = ParagraphStyle("title", fontSize=22, leading=26,
                               textColor=BLACK, alignment=TA_LEFT, spaceAfter=4)
        sub   = ParagraphStyle("sub", fontSize=11, leading=14, textColor=GREY)
        lbl   = ParagraphStyle("lbl", fontSize=8, leading=10,
                               textColor=GREY, alignment=TA_RIGHT)
        val   = ParagraphStyle("val", fontSize=11, leading=14,
                               textColor=BLACK, alignment=TA_RIGHT)

        left = [Paragraph("Financial Summary", title),
                Paragraph(f"{user.first_name} {user.last_name}", sub)]
        right = [Paragraph("FROM", lbl),
                 Paragraph(self._uk_date(date_from) or "all time", val),
                 Spacer(1, 2 * mm),
                 Paragraph("TO", lbl),
                 Paragraph(self._uk_date(date_to) or "today", val)]

        return [Table([[left, right]], colWidths=[120 * mm, 50 * mm],
                      style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))]

    def _stat_band(self, income, expense, count):
        """Stat cells"""
        cells = [[
            self._stat_cell("INCOME",       f"£{income:.2f}",  GREEN),
            self._stat_cell("EXPENSES",     f"£{expense:.2f}", RED),
            self._stat_cell("TRANSACTIONS", str(count),        BLACK),
        ]]
        return Table(cells, colWidths=[56.7 * mm] * 3, style=TableStyle([
            ("BOX",           (0, 0), (-1, -1), 0.5, GREY),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ]))

    @staticmethod
    def _stat_cell(label: str, value: str, value_color):
        """Grey label (income, expense, or transactions) and a coloured number"""
        return [
            Paragraph(label, ParagraphStyle(
                "sl", fontSize=9, leading=11, textColor=GREY)),
            Paragraph(f"<b>{value}</b>", ParagraphStyle(
                "sv", fontSize=18, leading=22, textColor=value_color)),
        ]

    def _transactions_table(self, rows):
        """5-column table: date / description / category / method / amount"""
        if not rows:
            return self._empty("No transactions in this range.")

        body = [["Date", "Description", "Category", "Method", "Amount"]]
        for t in rows:
            sign = "+" if t.type == "income" else "-"
            body.append([
                self._uk_date(t.date),
                t.description if len(t.description) <= 28 else t.description[:27] + "…",
                (t.category or "").title(),
                (t.method or "").replace("_", " ").title(),
                f"{sign}£{t.amount:.2f}",
            ])

        cmds = self._header_cmds() + self._body_cmds(font_size=9, padding=6) + [
            ("ALIGN",    (-1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ]
        # Colour the amount cell per row
        for i, t in enumerate(rows, start=1):
            cmds.append(("TEXTCOLOR", (-1, i), (-1, i),
                         GREEN if t.type == "income" else RED))

        return Table(body, colWidths=[24 * mm, 46 * mm, 30 * mm, 36 * mm, 34 * mm],
                     style=TableStyle(cmds), repeatRows=1)

    def _category_table(self, rows):
        """2-column expenses-by-category table"""
        by_cat: dict[str, float] = {}
        for t in rows:
            if t.type == "expense":
                by_cat[t.category] = by_cat.get(t.category, 0) + t.amount
        if not by_cat:
            return self._empty("No expenses in this range.")

        body = [["Category", "Amount"]]
        for cat, total in sorted(by_cat.items(), key=lambda x: -x[1]):
            body.append([cat.title(), f"£{total:.2f}"])

        cmds = self._header_cmds() + self._body_cmds() + [
            ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ]
        return Table(body, colWidths=[120 * mm, 50 * mm], style=TableStyle(cmds))

    def _method_table(self, rows):
        """3-column by-method table"""
        by_method: dict[str, dict[str, float]] = {}
        for t in rows:
            d = by_method.setdefault(t.method, {"income": 0.0, "expense": 0.0})
            d[t.type] += t.amount
        if not by_method:
            return self._empty("No payment data.")

        body = [["Method", "Income", "Expenses"]]
        for m, v in by_method.items():
            body.append([m.replace("_", " ").title(),
                         f"+£{v['income']:.2f}", f"-£{v['expense']:.2f}"])

        cmds = self._header_cmds() + self._body_cmds() + [
            ("TEXTCOLOR", (1, 1), (1, -1), GREEN),
            ("FONTNAME",  (1, 1), (1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (2, 1), (2, -1), RED),
            ("FONTNAME",  (2, 1), (2, -1), "Helvetica-Bold"),
        ]
        return Table(body, colWidths=[80 * mm, 45 * mm, 45 * mm], style=TableStyle(cmds))


    @staticmethod
    def _h2():
        return ParagraphStyle("h2", fontSize=14, textColor=BLACK,
                              spaceBefore=2, spaceAfter=2)

    @staticmethod
    def _uk_date(iso: str) -> str:
        """Change ISO format to UK format"""
        if not iso or len(iso) < 10:
            return iso or ""
        try:
            y, m, d = iso[:10].split("-")
            return f"{d}/{m}/{y}"
        except ValueError:
            return iso

    @staticmethod
    def _empty(message: str):
        """Use when a section has no data"""
        return Table([[message]], colWidths=[170 * mm], style=TableStyle([
            ("FONTSIZE",     (0, 0), (-1, -1), 10),
            ("TEXTCOLOR",    (0, 0), (-1, -1), GREY),
            ("BOX",          (0, 0), (-1, -1), 0.5, GREY),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

    @staticmethod
    def _header_cmds():
        """Header row"""
        return [
            ("TEXTCOLOR",     (0, 0), (-1, 0), GREY),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING",    (0, 0), (-1, 0), 8),
            ("LINEBELOW",     (0, 0), (-1, 0), 0.5, GREY),
        ]

    @staticmethod
    def _body_cmds(*, font_size: int = 10, padding: int = 8):
        """Body rows"""
        v = padding - 2
        return [
            ("FONTSIZE",      (0, 1), (-1, -1), font_size),
            ("TEXTCOLOR",     (0, 1), (0, -1), BLACK),
            ("LEFTPADDING",   (0, 0), (-1, -1), padding),
            ("RIGHTPADDING",  (0, 0), (-1, -1), padding),
            ("TOPPADDING",    (0, 1), (-1, -1), v),
            ("BOTTOMPADDING", (0, 1), (-1, -1), v),
            ("LINEBELOW",     (0, 1), (-1, -2), 0.25, GREY),
        ]