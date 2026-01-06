from classifier import TextClassifier

if __name__=="__main__":
    with open("blog.txt", "r", encoding="utf-8") as f:
        blog_txt = f.read()

    classifier = TextClassifier(threshold=0.4)
    categories = classifier.classify(blog_txt)

    print("🔹 Predicted Categories:")
    print(categories)
