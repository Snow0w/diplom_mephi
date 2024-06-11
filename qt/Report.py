from pandas import DataFrame
from numpy import asarray, round, sum
from fpdf import FPDF
from fpdf.fonts import FontFace
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from sklearn import pipeline
from umap import UMAP
import seaborn as sns
from PIL import Image
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from os.path import dirname, abspath, join

class Report:
    def __init__(self, df):
        self.df = df

    def make_report(self, fileName, timeMeasure, timeCreationFiles):
        filePath = dirname(abspath(fileName))
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(
                    40, 10,
                    "Classification report",
                    new_x="LMARGIN", new_y="NEXT",
                )
        pdf.set_font("helvetica", "", 14)
        pdf.cell(
                    40, 10,
                    timeCreationFiles.strftime('%H:%M %d.%m.%Y'),
                    new_x="LMARGIN", new_y="NEXT",
                )
        pdf.cell(
                    40, 10,
                    f'Source: {fileName}',
                    new_x="LMARGIN", new_y="NEXT",
                )

        pdf.cell(
                    40, 10,
                    f"Model working time in seconds: {timeMeasure}",
                    new_x="LMARGIN", new_y="NEXT",
                )
        pdf.cell(
                    40, 10,
                    f'Number of events in dataframe: {self.df.shape[0]}',
                    new_x="LMARGIN", new_y="NEXT",
                )
        prot_num = self.df.query("Label == 0").shape[0]
        elec_num = self.df.query("Label == 1").shape[0]
        self.__add_pie_chart(pdf, prot_num, elec_num)
        self.__add_UMAP_graph(pdf)
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(
                    40, 10,
                    'Statistical indicators of parameters',
                    new_x="LMARGIN", new_y="NEXT",
                )
        self.__add_tables(pdf)
        pdf.output(join(
            filePath,
            timeCreationFiles.strftime('Отчет_%H_%M_%d_%m_%Y.pdf')
            ))

    def __add_pie_chart(self, pdf, prot_num, elec_num):
        fig, ax = plt.subplots(figsize=(6, 4), subplot_kw=dict(aspect="equal"))
        recipe = [f'{prot_num} Protons',
                  f'{elec_num} Electrons']
        data = [float(x.split()[0]) for x in recipe]
        ingredients = [x.split()[-1] for x in recipe]
        def func(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f"{pct:.1f}%\n({absolute:d})"
        wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                          textprops=dict(color="w"))
        ax.legend(wedges, ingredients,
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=8, weight="bold")
        ax.set_title("Number of classified particles")
        canvas = FigureCanvas(fig)
        canvas.draw()
        img = Image.fromarray(asarray(canvas.buffer_rgba()))
        pdf.image(img, w=pdf.epw)

    def __add_UMAP_graph(self, pdf):
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(
                    40, 10,
                    'UMAP classification visualization',
                    new_x="LMARGIN", new_y="NEXT",
                )
        reducer = UMAP()
        sc = StandardScaler()
        embedding = reducer.fit_transform(
                sc.fit_transform(self.df.drop(columns=['Label']).to_numpy())
                )
        emb_df = DataFrame(embedding)
        emb_df['Label'] = self.df['Label']
        emb_prot = emb_df[emb_df.Label == 0]
        emb_elec = emb_df[emb_df.Label == 1]
        emb_prot = emb_prot.drop(columns='Label').copy()
        emp_elec = emb_elec.drop(columns='Label').copy()
        emb_prot = emb_prot.to_numpy() 
        emb_elec = emb_elec.to_numpy()
        fig = plt.figure(figsize=(10, 4), dpi=500)
        scatter_proton = plt.scatter(
            emb_prot[:, 0],
            emb_prot[:, 1],
            s = 1,
            color=sns.color_palette()[0],
            label='Protons'
            )
        scatter_elec = plt.scatter(
            emb_elec[:, 0],
            emb_elec[:, 1],
            s = 1,
            color=sns.color_palette()[1],
            label='Electrons'
            )
        legend = plt.legend(fontsize=14)
        for legobj in legend.legendHandles:
            legobj.set_sizes([100])
        canvas = FigureCanvas(fig)
        canvas.draw()
        img = Image.fromarray(asarray(canvas.buffer_rgba()))
        pdf.image(img, w=pdf.epw)

    def __add_tables(self, pdf):
        describe = self.df.describe().drop(columns=['Label', 'Unnamed: 0']).astype(str)
        colnames = list(describe)
        describe['Metric'] = describe.index.values
        cnt = 0
        pdf.set_font("helvetica", "", 10)
        for col in colnames:
            var = describe[['Metric', col]]
            COLUMNS = [list(var)]
            ROWS = var.values.tolist()
            DATA = COLUMNS + ROWS
            with pdf.table(
                headings_style = FontFace(emphasis="ITALICS", fill_color=(128, 128, 128)),
                cell_fill_mode="ROWS",
                text_align="CENTER",
                width=160,
            ) as table:
                for data_row in DATA:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)
            if cnt % 3 == 2:
                pdf.add_page()
            else:
                pdf.cell( 40, 10, "", new_x="LMARGIN", new_y="NEXT",)
            cnt +=1
