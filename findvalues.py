import numpy as np
from Utils import *
from findcontours import *
from loadstrels import *
from PIL import ImageGrab
import cv2
import time
# VERY IMPORTANT: Without it, the entire screen will not be captured
from ctypes import windll
# user32 = windll.user32
# user32.SetProcessDPIAware()

valueStrels = loadPlayerStrels()
suitStrels = loadSuitStrels()
publicSuitStrels = loadPublicSuitStrels()
potSizeStrels = loadPotSizeStrels()
publicstrels = loadPublicStrels()
chipCountStrels = loadChipCountStrels()

# Finds the players current suit
def findSuits(cardsImage):
    card1Suit = cardsImage[50:100, 10:50]
    card2Suit = cardsImage[58:100, 48:80]

    card1 = findElementInImage(card1Suit, suitStrels, False) + 1
    card2 = findElementInImage(card2Suit, suitStrels, False) + 1

    return card1, card2

def findCards(cardsImage):
    # Breaks down the image
    card1Value = cardsImage[8:50, 12:50]
    card2Value = cardsImage[20:58, 48:80]

    card1 = findElementInImage(card1Value, valueStrels, True) + 2
    card2 = findElementInImage(card2Value, valueStrels, True) + 2

    return card1, card2

def findChipSize(chipSizeImage, potSize, size):
    # Determine which structuring elements we need to use
    if potSize == 1:
        strels = potSizeStrels
    else:
        strels = chipCountStrels
    # Public pot sizes and player pot sizes require different erosions
    kernel = np.ones((size, size), dtype='uint8')
    chipSizeImage = cv2.dilate(chipSizeImage, kernel, iterations=1)
    return determinePotSize(chipSizeImage, strels, loadPlayerDollar())

def findPublicCards(publiccards):

    # All the submatrices for the cards use the same height
    height, width = publiccards.shape
    heightVar = int(height - (height / 2) - 20)
    cardValues = []
    cardSuits = []
    # Get submatrices of the whole cards to determine if there is a card at all
    wholeCard1 = publiccards[0:height, 0:int((width/5))]
    wholeCard2 = publiccards[0:height, int(width/5):int(2*width/5)]
    wholeCard3 = publiccards[0:height, int(2*width/5):int(3*width / 5)]
    wholeCard4 = publiccards[0:height, int(3* width / 5) + 10:int(4 * width / 5)]
    wholeCard5 = publiccards[0:height, int(4 * width / 5) + 15:int(width)]
    wholeCards = [wholeCard1, wholeCard2, wholeCard3, wholeCard4, wholeCard5]

    # Create submatrices of the values (cardN) and of the card's suit (cardNs)
    card1 = publiccards[0:heightVar, 0:int((width/5) - 60)]
    card1s = publiccards[heightVar - 2:heightVar + 38, 0:int((width/5) - 68)]
    card2 = publiccards[0:heightVar, int(width/5 + 5):int((width / 5) * 2 - 65)]
    card2s = publiccards[heightVar - 2:heightVar + 38, int(width/5 + 5):int((width / 5) * 2 - 64)]
    card3 = publiccards[0:heightVar, int((width / 5) * 2 + 10):int((width / 5) * 3 - 62)]
    card3s = publiccards[heightVar - 2:heightVar + 38, int((width / 5) * 2 + 7):int((width / 5) * 3 - 59)]
    card4 = publiccards[0:heightVar, int((width / 5) * 3 + 12):int((width / 5) * 4 - 56)]
    card4s = publiccards[heightVar - 2:heightVar + 38, int((width / 5) * 3 + 12):int((width / 5) * 4 - 56)]
    card5 = publiccards[0:heightVar, int((width / 5) * 4 + 20):int((width / 5) * 5 - 55)]
    card5s = publiccards[heightVar - 2:heightVar + 38, int((width / 5) * 4 + 16):int((width / 5) * 5 - 53)]
    # Put the values in a list for less verbose operations
    cardValueImages = [card1, card2, card3, card4, card5]
    cardSuitImages = [card1s, card2s, card3s, card4s, card5s]
    # Determine if the card exists. If it does, find out what it is
    i = 0
    for card in wholeCards:
        if isCard(card):
            cardValues.append(findElementInImage(cardValueImages[i], publicstrels, True) + 2)
            cardSuits.append(findElementInImage(cardSuitImages[i], publicSuitStrels, True) + 1)
        i = i + 1
    # If there aren't five cards, pad the rest with 0s
    if len(cardValues) < 5:
        for i in range (len(cardValues), 5):
            cardValues.append(0)
    if len(cardSuits) < 5:
        for i in range (len(cardSuits), 5):
            cardSuits.append(0)

    return cardValues, cardSuits

def isCard(image):
    im, contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        return True
    else:
        return False
