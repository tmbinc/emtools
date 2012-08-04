SECTIONS 
{
	. = 0x08019974;

	.atihandler : {
		*(.atihandler)
	}


	. = 0x0801B000;

	.text : {
		*(.text)
	}

}
