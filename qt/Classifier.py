from pandas import read_csv
from numpy import delete
from pickle import load
from time import time
from datetime import datetime
from os.path import dirname, abspath, join
from ClassificationReportException import ClassificationReportException
from WrongDataException import WrongDataException
from Report import Report


class Classifier:
    def __init__(self, name):
        self.fileName = name

    def classification(self):
        try:
            with open('model.pkl', 'rb') as f:
                model = load(f)
        except Exception:
            raise WrongDataException("Ошибка при загрузке модели")
        try:
            self.df = read_csv(self.fileName)
            self.timeMeasure = time()
            pred = model.predict(
                    delete(self.df.to_numpy(), obj=[28, 29, 19, 23], axis=1)
                    )
            self.timeMeasure = time() - self.timeMeasure
        except Exception:
            raise WrongDataException("Неправильный формат данных в файле")
        self.df['Label'] = pred
        prot = self.df.query('Label == 0').copy()
        elec = self.df.query('Label == 1').copy()
        prot.drop(columns=['Label'], inplace = True)
        elec.drop(columns=['Label'], inplace = True)
        filePath = dirname(abspath(self.fileName))
        self.timeCreationFiles = datetime.now()
        try:
            prot.to_csv(
                    join(
                        filePath,
                        self.timeCreationFiles.strftime('Протоны_%H_%M_%d_%m_%Y.csv')
                        ), encoding = 'utf-8'
                    )
            elec.to_csv(
                    join(
                        filePath,
                        self.timeCreationFiles.strftime('Электроны_%H_%M_%d_%m_%Y.csv')
                        ), encoding = 'utf-8'
                    )
        except Exception:
            raise Exception("Не удалось сохранить результат")

    def classification_with_report(self):
        self.classification()
        try:
            report = Report(self.df)
            report.make_report(self.fileName, self.timeMeasure, self.timeCreationFiles)
        except Exception:
            raise ClassificationReportException('Ошибка при создании отчета')







        



