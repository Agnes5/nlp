from sklearn.metrics import precision_recall_fscore_support


def main():
    f1 = open('test_result', 'r')
    f2 = open('test_value', 'r')

    result = f1.readlines()
    value = f2.readlines()

    result_num = []
    value_num = []

    for r in result:
        if '0' in r:
            result_num.append(0)
        else:
            result_num.append(1)

    for v in value:
        if '0' in v:
            value_num.append(0)
        else:
            value_num.append(1)

    p, r, f, _ = precision_recall_fscore_support(value_num, result_num, average='weighted')
    print(p)
    print(r)
    print(f)


if __name__ == "__main__":
    main()
