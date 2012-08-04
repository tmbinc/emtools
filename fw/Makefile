CROSS=arm-none-eabi-

CFLAGS=-mcpu=cortex-m3 -mthumb -O2

SOURCES=overlay.c import.s

all: flash_patch.ebl

flash_patch.ebl: flash_patch.bin
	python ../tools/flash2ebl.py flash_patch.bin flash_patch.ebl

flash_patch.bin: fw.srec flash.srec
	head -n-1 flash.srec > flashfw.srec
	cat fw.srec >> flashfw.srec
	$(CROSS)objcopy -I srec flashfw.srec -O binary flash_patch.bin

flash.srec:
	$(CROSS)objcopy -I binary -O srec flash.bin flash.srec --change-addresses 0x08000000

fw.srec: fw.elf
	$(CROSS)objcopy -S -O srec fw.elf fw.srec

fw.elf: $(SOURCES)
	$(CROSS)gcc $(CFLAGS) $(SOURCES)  -nostdlib -Wl,-Toverlay.ld -o fw.elf
	
clean:
	rm -f fw.bin fw.elf flash.srec fw.srec flash_patch.bin flash_patch.ebl flashfw.srec

