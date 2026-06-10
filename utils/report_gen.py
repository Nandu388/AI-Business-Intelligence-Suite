import io
import pandas as pd
from fpdf import FPDF


# =====================================================
# EXCEL EXPORT
# =====================================================
def to_excel_bytes(sheets_dict):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        for sheet_name, df in sheets_dict.items():

            try:

                clean_name = str(sheet_name)[:31]

                if isinstance(df, pd.DataFrame):

                    df.to_excel(
                        writer,
                        sheet_name=clean_name,
                        index=False
                    )

            except:
                pass

    output.seek(0)

    return output.getvalue()


# =====================================================
# CLEAN TEXT
# =====================================================
def clean_text(text):

    text = str(text)

    replacements = {

        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "₹": "Rs",
        "€": "EUR",
        "£": "GBP"
    }

    for k, v in replacements.items():

        text = text.replace(k, v)

    return text.encode(
        "latin-1",
        "ignore"
    ).decode("latin-1")


# =====================================================
# PDF CLASS
# =====================================================
class PDF(FPDF):

    def header(self):

        self.set_font(
            "Helvetica",
            "B",
            18
        )

        self.cell(
            0,
            10,
            "AI BI REPORT",
            ln=True,
            align="C"
        )

        self.ln(5)

    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "",
            10
        )

        self.cell(
            0,
            10,
            f"Page {self.page_no()}",
            align="C"
        )


# =====================================================
# PDF EXPORT
# =====================================================
def to_pdf_bytes(sections):

    pdf = PDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # =================================================
    # LOOP THROUGH SECTIONS
    # =================================================
    for sec in sections:

        try:

            title = clean_text(
                sec.get("title", "")
            )

            # -----------------------------------------
            # TITLE
            # -----------------------------------------
            pdf.set_font(
                "Helvetica",
                "B",
                14
            )

            pdf.multi_cell(
                0,
                10,
                title
            )

            pdf.ln(2)

            # -----------------------------------------
            # KEY VALUE DATA
            # -----------------------------------------
            if "kv" in sec:

                pdf.set_font(
                    "Helvetica",
                    "",
                    11
                )

                for k, v in sec["kv"].items():

                    line = (
                        f"{clean_text(k)} : "
                        f"{clean_text(v)}"
                    )

                    pdf.multi_cell(
                        0,
                        8,
                        line
                    )

            # -----------------------------------------
            # DATAFRAME
            # -----------------------------------------
            if "df" in sec:

                df = sec["df"]

                if isinstance(df, pd.DataFrame):

                    pdf.set_font(
                        "Courier",
                        "",
                        8
                    )

                    preview = df.head(15)

                    text = clean_text(
                        preview.to_string(index=False)
                    )

                    pdf.multi_cell(
                        0,
                        5,
                        text
                    )

            pdf.ln(8)

        except:
            pass

    # =================================================
    # FINAL PDF OUTPUT
    # =================================================
    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, bytearray):

        return bytes(pdf_output)

    return pdf_output.encode(
        "latin-1"
    )