TARGET      := sokoban4
BUILD       := build
LIBBUTANO   := butano/butano
LIBBUTANOABS:= $(realpath $(LIBBUTANO))
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
