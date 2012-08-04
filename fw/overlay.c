
void xprintf(int t, const char *fmt, ...);
void ReadToken(char *dest, int x, int y, int size);

#define TOKEN_PASSWORD 0x10,0x7F

void test(void)
{
	char buf[128];
	xprintf(0x21, "Hello World!\r\n");
	ReadToken(buf, TOKEN_PASSWORD, 8);
	xprintf(0x21, "password = '%s'\r\n", buf);
}

// put our function as the "ATI" handler by overwriting the table entry

void __attribute__((section(".atihandler"))) (*atihandler)() = &test;
