from classifier import TextClassifier

if __name__=="__main__":
    
    with open("blog.txt", "r", encoding="utf-8")as f:
        blog_txt= f.read()
    classifier=TextClassifier()
    categories= classifier.classify(blog_txt)
    print(categories)
