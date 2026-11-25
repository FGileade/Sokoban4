TARGET      := sokoban4
BUILD       := build
LIBBUTANO   ?= $(CURDIR)/butano/butano
export LIBBUTANO
LIBBUTANOABS:= $(LIBBUTANO)
PYTHON      := python3
SOURCES     := src
INCLUDES    := include
DATA        :=
GRAPHICS    := graphics
AUDIO       :=
DMGAUDIO    :=
ROMTITLE    := SOKOBAN4
ROMCODE     := SKB4
USERFLAGS   :=
USERCXXFLAGS:=
USERASFLAGS :=
USERLDFLAGS :=
USERLIBDIRS :=
USERLIBS    :=
DEFAULTLIBS :=

include $(LIBBUTANO)/butano.mak
