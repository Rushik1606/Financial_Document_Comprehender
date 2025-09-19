from typing import List, Tuple
import io
import re

import pandas as pd
import pdfplumber


def parse_pdf(file_like: io.BytesIO) -> Tuple[List[str], List[pd.DataFrame]]:
	texts: List[str] = []
	tables: List[pd.DataFrame] = []
	with pdfplumber.open(file_like) as pdf:
		for page in pdf.pages:
			text = page.extract_text() or ""
			if text.strip():
				texts.append(text)
			tbls = page.extract_tables()
			for tbl in tbls or []:
				try:
					df = pd.DataFrame(tbl)
					if df.shape[0] > 1 and df.iloc[0].isnull().sum() == 0:
						df.columns = df.iloc[0]
						df = df.iloc[1:].reset_index(drop=True)
					tables.append(clean_table(df))
				except Exception:
					continue
	return texts, tables


def parse_excel(file_like: io.BytesIO) -> Tuple[List[str], List[pd.DataFrame]]:
	texts: List[str] = []
	tables: List[pd.DataFrame] = []
	xls = pd.ExcelFile(file_like)
	for sheet in xls.sheet_names:
		df = xls.parse(sheet_name=sheet, header=0)
		df = clean_table(df)
		tables.append(df)
		texts.append(df_to_text(df, title=f"Sheet: {sheet}"))
	return texts, tables


def clean_table(df: pd.DataFrame) -> pd.DataFrame:
	df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
	df.columns = [str(c).strip() for c in df.columns]
	return df


def df_to_text(df: pd.DataFrame, title: str = "Table") -> str:
	repr_df = df.copy()
	return f"{title}\n" + repr_df.to_csv(index=False, sep='\t')


def chunk_texts(texts: List[str], max_tokens: int = 400) -> List[str]:
	chunks: List[str] = []
	for t in texts:
		parts = re.split(r"\n\n+", t)
		current = ""
		for p in parts:
			if len(current) + len(p) > max_tokens:
				if current.strip():
					chunks.append(current.strip())
				current = p
			else:
				current += ("\n\n" if current else "") + p
		if current.strip():
			chunks.append(current.strip())
	return chunks
