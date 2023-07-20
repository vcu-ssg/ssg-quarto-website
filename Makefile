.SILENT:

ifeq ($(OS),Windows_NT)
SHELL := pwsh.exe
.SHELLFLAGS := -NoProfile -Command
endif


default:
	type Makefile

bios:
	@echo "Generating about pages using gsheet data"
	cd code; ssg-webtool bios
	@echo "Quarto rendering website"
	cd website; quarto render

