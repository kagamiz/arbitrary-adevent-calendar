from database import engine
from models import Base

if __name__ == "__main__":
    print("DBのテーブルを作成します...")
    Base.metadata.create_all(bind=engine)
    print("完了しました。") 
