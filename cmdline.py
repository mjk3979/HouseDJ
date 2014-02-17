def inputChoice(lst):
	if lst == None or lst == []:
		return None
	while True:
		i = 0
		for c in lst:
			print(str(i+1) + ": " + str(c))
			i += 1
		choice = int(input("Choice: "))
		if choice >= 1 and choice <= len(lst):
			return (choice - 1, lst[choice-1])
