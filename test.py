from aigoumid import *
from info import *
from aigoumid import *

def main():
    test_ag = aigoumid()
    ret = test_ag.check_price(Price)
    print(ret)
    ret2 = test_ag.cal_order(Order)
    print(ret2)

if __name__ == '__main__':
    main()

