import time
import serial
import struct

usage_id = ["NONE", "ERO", "PF", "ERR", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "ENTER", "ESC", "BKSPC", "TAB", "SPACE", "-", "+", "{", "}", "|", "~", ":", "\"", "HANKAKU", "<", ">", "?", "CAPS", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "PRTSCR", "SCRLK", "PAUSE", "INSERT", "HOME", "PGUP", "DEL", "END", "PGDN", "RIGHT", "LEFT", "DOWN", "UP", "NUMLK", "/", "*", "-", "+", "ENTER", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "\\", "APP", "POWER", "=", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "EXEC", "HELP", "SELECT", "STOP", "AGAIN", "UNDO", "CUT", "COPY", "PASTE", "FIND", "MUTE", "VOLUP", "VOLDN", "CAPSLK", "NUMLK", "SCKLK", ",", "NA", "\\", "HIRAGANA", "ROMAJI", "NA", "COVT", "NONCNVT", "NA", "NA", "NA", "KANA", "EISU", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "LCTRL", "LSHIFT", "LALT", "LWIN", "RCTRL", "RSHIFT", "RALT", "RWIN"]
led_status = [False, False, False]

port = serial.Serial("COM22", 115200)
port.flush()

def wink_led():
	while True:
		send_cmd = [0x57, 0xAB, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAC, 0x20]
		port.write(send_cmd)
		time.sleep(0.5)
		send_cmd[7] = 0x01
		port.write(send_cmd)
		time.sleep(0.5)
		send_cmd[7] = send_cmd[7] << 1
		port.write(send_cmd)
		time.sleep(0.5)
		send_cmd[7] = send_cmd[7] << 1
		port.write(send_cmd)
		time.sleep(0.5)

#	0: Num Lock, 1: Caps Lock, 2: Scroll Lock
def switch_led(id):
	led_status[id] = not bool(led_status[id])
	send_cmd = [0x57, 0xAB, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAC, 0x20]
	send_cmd[7] = (int(led_status[2]) << 2) + (int(led_status[1]) << 1) + int(led_status[0])
	port.write(send_cmd)


def parse_keys():
	parsed = "["
	for i in range(6):
		r = port.read(1)
		if (int.from_bytes(r, 'big') == 83):
			switch_led(0)
		elif (int.from_bytes(r, 'big') == 57):
			switch_led(1)
		elif (int.from_bytes(r, 'big') == 71):
			switch_led(2)
		#print(str(i) + ": " + r.hex())
		#print(int.from_bytes(r, 'big'))
		parsed += usage_id[int.from_bytes(r, 'big')]
		parsed += " "
	parsed += "]"
	print(parsed)
	#print(port.read(2).hex())

def sync_header(r):
	while True:
		while (port.in_waiting > 0):
			if r == b'W':
				if port.read(1) == b'\xab':
					r = port.read(1) 
					if r == b'\x82':
						time.sleep(0.01)
						#print("NULL")
						return b'W'
					else:
						port.read(3)
						r = port.read(1)
						return r
			else:
				r = port.read(1)

#wink_led()	#for led test

while True:
	r = b'\x00'
	if port.in_waiting > 0:
		r = port.read(1)
	while (port.in_waiting > 0):
		r = sync_header(r) 
		if r != b'W':
			#print("KEYEVT")
			parse_keys()
			r = port.read(1)