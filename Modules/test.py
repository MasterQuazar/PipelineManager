import maya.cmds as mc
from multiprocessing import Process


def test_function():
	print("hello world!")


p = Process(target=test_function)
p.start()
p.join()