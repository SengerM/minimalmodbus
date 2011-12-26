#!/usr/bin/env python
#
#   Copyright 2011 Jonas Berg
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

"""

.. moduleauthor:: Jonas Berg <pyhys@users.sourceforge.net>

test_minimalmodbus: Unittests for minimalmodbus

This Python file was changed (committed) at $Date$, 
which was $Revision$.

"""

__author__  = "Jonas Berg"
__email__   = "pyhys@users.sourceforge.net"
__license__ = "Apache License, Version 2.0"

__revision__  = "$Rev$"
__date__      = "$Date$"

import unittest
import minimalmodbus


####################
# Payload handling #
####################

class TestEmbedPayload(unittest.TestCase):

    knownValues=[
    (1, 16, 'ABC', '\x01\x10ABC<E'),
    (0, 5, 'hjl', '\x00\x05hjl\x8b\x9d'),
    (2, 2, '123', '\x02\x02123X\xc2'),
    ]
    
    def testKnownValues(self):
        for address, functioncode, inputstring, knownresult in self.knownValues:
            
            result = minimalmodbus._embedPayload(address, functioncode, inputstring)
            self.assertEqual(result, knownresult)

    def testWrongSlaveaddressValue(self):
        self.assertRaises(ValueError, minimalmodbus._embedPayload, 248, 16, 'ABC')    
        self.assertRaises(ValueError, minimalmodbus._embedPayload, -1, 16, 'ABC')    
       
    def testSlaveaddressNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1.0, 16, 'ABC') 
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 'DEF', 16, 'ABC') 

    def testWrongFunctioncodeValue(self):
        self.assertRaises(ValueError, minimalmodbus._embedPayload, 1, 222, 'ABC') 
        self.assertRaises(ValueError, minimalmodbus._embedPayload, 1, -1, 'ABC') 
        
    def testFunctioncodeNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, 1.0, 'ABC') 
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, '1', 'ABC')
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, [1], 'ABC')
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, None, 'ABC')

    def testPayloadNotString(self):
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, 16, 1) 
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, 16, 1.0) 
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, 16, ['ABC']) 
        self.assertRaises(TypeError, minimalmodbus._embedPayload, 1, 16, None) 

class TestExtractPayload(unittest.TestCase):

    knownValues=TestEmbedPayload.knownValues

    def testKnownValues(self):
        for address, functioncode, knownresult, inputstring in self.knownValues:
            
            result = minimalmodbus._extractPayload(inputstring, address, functioncode )
            self.assertEqual(result, knownresult)
            
    def testTooShortMessage(self):
        self.assertRaises(ValueError, minimalmodbus._extractPayload, 'A', 2, 2) 

    def testWrongCrc(self):
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc3', 2, 2) 
    
    def testErrorindicationFromSlave(self):
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x82123q\x02', 2, 2) 
            
    def testWrongSlaveAddress(self):
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 3, 2)
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 248, 2)
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', -1, 2)
        
    def testSlaveaddressNotInteger(self):    
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2.0, 2) 
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', '2', 2) 
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', [2], 2) 
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', None, 2) 
        
    def testWrongFunctionCode(self):
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, 3)  
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x72123B\x02', 2, 2) 
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, -1)
        self.assertRaises(ValueError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, 128)
  
    def testFunctionCodeNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, 2.0)   
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, '2')   
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, [2])
        self.assertRaises(TypeError, minimalmodbus._extractPayload, '\x02\x02123X\xc2', 2, None)      
    
##############################
# String and num conversions #
##############################

class TestNumToOneByteString(unittest.TestCase):

    knownValues=[
    (7, '\x07' ), 
    ]

    def testKnownValues(self):
        for inputvalue, knownstring in self.knownValues:
            
            resultstring = minimalmodbus._numToOneByteString( inputvalue )
            self.assertEqual(resultstring, knownstring)     

    def testKnownLoop(self):
        for x in range(256):
            knownstring = chr(x)
            resultstring = minimalmodbus._numToOneByteString( x )
            
            self.assertEqual(resultstring, knownstring)       

    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._numToOneByteString, 1.0)
        self.assertRaises(TypeError, minimalmodbus._numToOneByteString, '1')
        self.assertRaises(TypeError, minimalmodbus._numToOneByteString, [1])
        self.assertRaises(TypeError, minimalmodbus._numToOneByteString, None)

    def testNegativeInput(self):
        self.assertRaises(ValueError, minimalmodbus._numToOneByteString, -1)

    def testTooLargeInput(self):
        self.assertRaises(ValueError, minimalmodbus._numToOneByteString, 256)


class TestNumToTwoByteString(unittest.TestCase):

    knownValues=[
    (77.0, 1, False, '\x03\x02' ), 
    (77.0, 1, True,  '\x02\x03' ), 
    (770,  0, False, '\x03\x02' ), 
    (770,  0, True,  '\x02\x03' ), 
    ]

    def testKnownValues(self):
        for inputvalue, numberOfDecimals, LsbFirst, knownstring in self.knownValues:
            
            resultstring = minimalmodbus._numToTwoByteString(inputvalue, numberOfDecimals, LsbFirst)
            self.assertEqual(resultstring, knownstring)      

    def testNumberofdecimalsNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._numToTwoByteString, 77, 1.0, False)

    def testNegativeNumberofdecimals(self):
        self.assertRaises(ValueError, minimalmodbus._numToTwoByteString, 77, -1, False)

    def testNegativeValue(self):
        self.assertRaises(ValueError, minimalmodbus._numToTwoByteString, -77, 1, False)

    def testTooLargeValue(self):
        self.assertRaises(ValueError, minimalmodbus._numToTwoByteString, 77000, 0, False)
        self.assertRaises(ValueError, minimalmodbus._numToTwoByteString, 77, 4, False)

    def testLsbfirstNotBoolean(self):
        self.assertRaises(TypeError, minimalmodbus._numToTwoByteString, 77, 1, '1')
        self.assertRaises(TypeError, minimalmodbus._numToTwoByteString, 77, 1, 1)


class TestTwoByteStringToNum(unittest.TestCase):

    knownValues=[
    ('\x03\x02', 1, 77.0), 
    ('\x03\x02', 0, 770 ), 
    ]

    def testKnownValues(self):
        for inputstring, numberOfDecimals, knownvalue in self.knownValues:
            resultvalue = minimalmodbus._twoByteStringToNum(inputstring, numberOfDecimals)
            self.assertEqual(resultvalue, knownvalue)      

    def testInputNotStringType(self):        
        self.assertRaises(TypeError, minimalmodbus._twoByteStringToNum, 1, 1)

    def testInputStringTooLong(self):
        self.assertRaises(ValueError, minimalmodbus._twoByteStringToNum, 'ABC', 1)

    def testInputStringTooShort(self):
        self.assertRaises(ValueError, minimalmodbus._twoByteStringToNum, 'A', 1)

    def testNumberofdecimalsNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._twoByteStringToNum, 'AB', 1.0)
        self.assertRaises(TypeError, minimalmodbus._twoByteStringToNum, 'AB', '1')
        self.assertRaises(TypeError, minimalmodbus._twoByteStringToNum, 'AB', [1])
        self.assertRaises(TypeError, minimalmodbus._twoByteStringToNum, 'AB', None)

    def testNegativeNumberofdecimals(self):
        self.assertRaises(ValueError, minimalmodbus._twoByteStringToNum, 'AB', -1)


class TestSanityTwoByteString(unittest.TestCase):

    def testKnownValuesLoop(self):
        for x in range(0x10000):
        
            resultvalue = minimalmodbus._twoByteStringToNum( minimalmodbus._numToTwoByteString(x) )
            self.assertEqual(resultvalue, x)       

class TestBitResponseToValue(unittest.TestCase):            

    def testKnownValues(self):
        self.assertEqual(minimalmodbus._bitResponseToValue('\x00'), 0) 
        self.assertEqual(minimalmodbus._bitResponseToValue('\x01'), 1) 

    def testInputWrongValues(self): 
        self.assertRaises(ValueError, minimalmodbus._bitResponseToValue, 'ABC' )

    def testInputNotStringType(self):     
        self.assertRaises(TypeError, minimalmodbus._bitResponseToValue, 1 )
        self.assertRaises(TypeError, minimalmodbus._bitResponseToValue, 1.0 )
        self.assertRaises(TypeError, minimalmodbus._bitResponseToValue, ['\x00'] )
        self.assertRaises(TypeError, minimalmodbus._bitResponseToValue, None )
        
        
class TestCreateBitPattern(unittest.TestCase):           

    knownValues=[
    (5,  0, '\x00\x00'), 
    (5,  1, '\xff\x00' ), 
    (15, 0, '\x00'), 
    (15, 1, '\x01'), 
    ]

    def testKnownValues(self):
        for functioncode, value, knownresult in self.knownValues:
            resultvalue = minimalmodbus._createBitpattern(functioncode, value)
            self.assertEqual(resultvalue, knownresult) 
                
    def testWrongFunctionCode(self):
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 16, 1)  
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, -1, 1)  
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 128, 1)  
 
    def testFunctionCodeNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 15.0, 1) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, '15', 1) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, [15], 1) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, None, 1) 
 
    def testWrongValue(self):
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 5, 2)  
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 5, 222) 
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 5, -1) 
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 15, 2) 
        self.assertRaises(ValueError, minimalmodbus._createBitpattern, 15, -1) 
 
    def testValueNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 5, 1.0)  
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 5, 0.0) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 15, 1.0)  
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 15, 0.0) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 5, '1') 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 15, '1') 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 5, [1]) 
        self.assertRaises(TypeError, minimalmodbus._createBitpattern, 5, None) 
        
        
####################    
# Bit manipulation #
####################    
    
class TestSetBitOn(unittest.TestCase):

    knownValues=[
    (4,0,5),
    (4,1,6),
    (1,1,3),
    ]

    def testKnownValues(self):
        for x, bitnum, knownresult in self.knownValues:
            
            result = minimalmodbus._setBitOn(x, bitnum)
            self.assertEqual(result, knownresult)

    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._setBitOn, 1.0, 1)
        self.assertRaises(TypeError, minimalmodbus._setBitOn, '1', 1)
        self.assertRaises(TypeError, minimalmodbus._setBitOn, [1], 1)
        self.assertRaises(TypeError, minimalmodbus._setBitOn, None, 1)
        self.assertRaises(TypeError, minimalmodbus._setBitOn, 1, '1')
        self.assertRaises(TypeError, minimalmodbus._setBitOn, 1, 1.0)
        self.assertRaises(TypeError, minimalmodbus._setBitOn, 1, [1])
        self.assertRaises(TypeError, minimalmodbus._setBitOn, 1, None)

    def testNegativeInput(self):
        self.assertRaises(ValueError, minimalmodbus._setBitOn, 1, -1)        
        self.assertRaises(ValueError, minimalmodbus._setBitOn, -2, 1)     
               
               
class TestXOR(unittest.TestCase):

    knownValues=[
    (1,1,0),
    (2,1,3),
    (5,1,4),
    ]

    def testKnownValues(self):
        for int1, int2, knownresult in self.knownValues:
            
            result = minimalmodbus._XOR(int1, int2)
            self.assertEqual(result, knownresult)        
           
    def testKnownLoop(self):
        for i in range(10):
            for k in range(10):
                
                knownresult = i ^ k
                result = minimalmodbus._XOR(i, k)
                self.assertEqual(result, knownresult) 
    
    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._XOR, '1', 1)
        self.assertRaises(TypeError, minimalmodbus._XOR, 1.0, 1)
        self.assertRaises(TypeError, minimalmodbus._XOR, [1], 1)
        self.assertRaises(TypeError, minimalmodbus._XOR, None, 1)
        self.assertRaises(TypeError, minimalmodbus._XOR, 1, '1')
        self.assertRaises(TypeError, minimalmodbus._XOR, 1, [1])
        self.assertRaises(TypeError, minimalmodbus._XOR, 1, 1.0)
        self.assertRaises(TypeError, minimalmodbus._XOR, 1, None)

    def testNegativeInput(self):
        self.assertRaises(ValueError, minimalmodbus._XOR, 1, -1)        
        self.assertRaises(ValueError, minimalmodbus._XOR, -1, 1)         
    
    
class TestRightshift(unittest.TestCase):

    knownValues=[
    (9,4,1),
    (5,2,1),
    (6,3,0),
    ]

    def testKnownValues(self):
        for x, knownshifted, knowncarry in self.knownValues:
            
            resultshifted, resultcarry = minimalmodbus._rightshift(x)
            
            self.assertEqual(resultshifted, knownshifted)       
            self.assertEqual(resultcarry, knowncarry)      
           
    def testKnownLoop(self):
        for x in range(256):
            
            knownshifted = x >> 1
            knowncarry = x & 1
            resultshifted, resultcarry = minimalmodbus._rightshift(x)
            
            self.assertEqual(resultshifted, knownshifted)       
            self.assertEqual(resultcarry, knowncarry) 
   
    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._rightshift, '1')
        self.assertRaises(TypeError, minimalmodbus._rightshift, [1])
        self.assertRaises(TypeError, minimalmodbus._rightshift, 1.0)
        self.assertRaises(TypeError, minimalmodbus._rightshift, None)

    def testNegativeInput(self):
        self.assertRaises(ValueError, minimalmodbus._rightshift, -1)  
        

############################    
# Error checking functions #    
############################

class TestCalculateCrcString(unittest.TestCase):

    knownValues=[
    ('\x02\x07','\x41\x12'), # Example from MODBUS over Serial Line Specification and Implementation Guide V1.02 
    ('ABCDE', '\x0fP'),
    ]

    def testKnownValues(self):
        for inputstring, knowncrc in self.knownValues:
            resultcrc = minimalmodbus._calculateCrcString(inputstring)
            self.assertEqual(resultcrc, knowncrc)     

    def testNotStringInput(self):
        self.assertRaises(TypeError, minimalmodbus._calculateCrcString, 123)
        self.assertRaises(TypeError, minimalmodbus._calculateCrcString, 1.0)
        self.assertRaises(TypeError, minimalmodbus._calculateCrcString, None)
        self.assertRaises(TypeError, minimalmodbus._calculateCrcString, ['ABC'])

        
class TestCheckFunctioncode(unittest.TestCase):    
    
    def testCorrectFunctioncode(self):
        minimalmodbus._checkFunctioncode( 7, [7, 8] )
        
    def testCorrectFunctioncodeNoRange(self):
        minimalmodbus._checkFunctioncode( 7, None )    
        
    def testWrongFunctioncode(self):
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, 4, [7, 8])

    def testWrongFunctioncodeNoRange(self):   
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, 1000, None)
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, -1, None)

    def testWrongFunctioncodeType(self):
        self.assertRaises(TypeError, minimalmodbus._checkFunctioncode, '7', [7, 8])
        self.assertRaises(TypeError, minimalmodbus._checkFunctioncode, 7.5, [7, 8])
        self.assertRaises(TypeError, minimalmodbus._checkFunctioncode, 7.0, [7, 8])
        self.assertRaises(TypeError, minimalmodbus._checkFunctioncode, [7], [7, 8])
        self.assertRaises(TypeError, minimalmodbus._checkFunctioncode, None, [7, 8])

    def testWrongFunctioncodeListValues(self):
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, -1, [-1, 8])
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, 128, [7, 128])

    def testWrongListType(self):
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, 7)
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, 'ABC')
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, (7, 8))
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, 4, [7, -23])
        self.assertRaises(ValueError, minimalmodbus._checkFunctioncode, 4, [7, 128])
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, [7, 'ABC'])
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, [7, None])
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, [7, [8]])
        self.assertRaises(TypeError,  minimalmodbus._checkFunctioncode, 4, [7.5, 8])


class TestCheckSlaveaddress(unittest.TestCase):  

    def testKnownValues(self):
        minimalmodbus._checkSlaveaddress( 0 )
        minimalmodbus._checkSlaveaddress( 1 )
        minimalmodbus._checkSlaveaddress( 10 )
        minimalmodbus._checkSlaveaddress( 247 )

    def testWrongValues(self):
        self.assertRaises(ValueError, minimalmodbus._checkSlaveaddress, -1)
        self.assertRaises(ValueError, minimalmodbus._checkSlaveaddress, 248)
        
    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._checkSlaveaddress, 1.0)
        self.assertRaises(TypeError, minimalmodbus._checkSlaveaddress, '1')
        self.assertRaises(TypeError, minimalmodbus._checkSlaveaddress, [1])
        self.assertRaises(TypeError, minimalmodbus._checkSlaveaddress, None)
        

class TestCheckRegisteraddress(unittest.TestCase):  
    
    def testKnownValues(self):
        minimalmodbus._checkRegisteraddress( 0 )
        minimalmodbus._checkRegisteraddress( 1 )
        minimalmodbus._checkRegisteraddress( 10 )
        minimalmodbus._checkRegisteraddress( 65535 )

    def testWrongValues(self):
        self.assertRaises(ValueError, minimalmodbus._checkRegisteraddress, -1)
        self.assertRaises(ValueError, minimalmodbus._checkRegisteraddress, 65536)
        
    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, 1.0)
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, '1')
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, [1])
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, None)
        
    
class TestCheckResponseNumberOfBytes(unittest.TestCase):    
    
    def testCorrectNumberOfBytes(self):
        minimalmodbus._checkResponseByteCount('\x02\x03\x02')
        
    def testWrongNumberOfBytes(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseByteCount, '\x03\x03\x02')
        self.assertRaises(ValueError, minimalmodbus._checkResponseByteCount, 'ABC')

    def testNotStringInput(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseByteCount, 123)
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, ['ABC'])
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, 1.0)
        self.assertRaises(TypeError, minimalmodbus._checkRegisteraddress, None)
        
        
class TestCheckResponseRegisterAddress(unittest.TestCase):    
       
    def testCorrectResponseRegisterAddress(self):
        minimalmodbus._checkResponseRegisterAddress( '\x00\x2d\x00\x58', 45)
        minimalmodbus._checkResponseRegisterAddress( '\x00\x18\x00\x01', 24)
        minimalmodbus._checkResponseRegisterAddress( '\x00\x47\xff\x00', 71)
        minimalmodbus._checkResponseRegisterAddress( '\x00\x48\x00\x01', 72)
        
    def testWrongResponseRegisterAddress(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', 46)

    def testTooShortString(self):        
        self.assertRaises(ValueError, minimalmodbus._checkResponseRegisterAddress, '\x00', 46)
        
    def testNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, 1, 45)    
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, 1.0, 45)  
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, ['\x00\x2d\x00\x58'], 45)   
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, None, 45)  

    def testWrongAddress(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', -2)     
        self.assertRaises(ValueError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', 65536)   
        
    def testAddressNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', 45.0)     
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', '45')  
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', [45])  
        self.assertRaises(TypeError, minimalmodbus._checkResponseRegisterAddress, '\x00\x2d\x00\x58', None)  

class TestCheckResponseNumberOfRegisters(unittest.TestCase):    
        
    def testCorrectResponseNumberOfRegisters(self):
        minimalmodbus._checkResponseNumberOfRegisters( '\x00\x18\x00\x01', 1 )
        minimalmodbus._checkResponseNumberOfRegisters( '\x00#\x00\x01', 1 )
        minimalmodbus._checkResponseNumberOfRegisters( '\x00\x34\x00\x02', 2 )
        
    def testWrongResponseNumberOfRegisters(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseNumberOfRegisters, '\x00#\x00\x01', 4 )

    def testTooShortString(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseNumberOfRegisters, '\x00', 1 )

    def testNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, 1, 1 )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, 1.0, 1 )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, None, 1 )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, ['\x00#\x00\x01'], 1 )
    
    def testWrongResponseNumberOfRegistersRange(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x00', 0 )
        self.assertRaises(ValueError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', -1 )
        self.assertRaises(ValueError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', 65536 )

    def testNumberOfRegistersNotInteger(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', [1] )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', 1.0 )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', 'ABC' )
        self.assertRaises(TypeError, minimalmodbus._checkResponseNumberOfRegisters, '\x00\x18\x00\x01', None )

class TestCheckResponseWriteData(unittest.TestCase):    
  
    def testCorrectResponseWritedata(self):
        minimalmodbus._checkResponseWriteData('\x00\x2d\x00\x58', '\x00\x58')
        minimalmodbus._checkResponseWriteData('\x00\x2d\x00\x58', minimalmodbus._numToTwoByteString(88))
        minimalmodbus._checkResponseWriteData('\x00\x47\xff\x00', '\xff\x00')
        minimalmodbus._checkResponseWriteData('\x00\x47\xff\x00', minimalmodbus._numToTwoByteString(65280))
        minimalmodbus._checkResponseWriteData('\x00\x2d\x00\x58ABCDEFGHIJKLMNOP', '\x00\x58')

    def testWrongResponseWritedata(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', '\x00\x59')
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', minimalmodbus._numToTwoByteString(89))    
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x47\xff\x00', '\xff\x01')
        
    def testNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, 1, '\x00\x58')  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, 1.0, '\x00\x58')  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, ['\x00\x2d\x00\x58'], '\x00\x58')  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, None, '\x00\x58')  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', 1)  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', 1.0)  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', ['\x00\x58'])  
        self.assertRaises(TypeError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', None)  
        
    def testTooShortString(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x58', '\x00\x58')  
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '', '\x00\x58')  
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', '\x58')  
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', '')  
    
    def testTooLongString(self):
        self.assertRaises(ValueError, minimalmodbus._checkResponseWriteData, '\x00\x2d\x00\x58', '\x00\x58\x00')  
        

class TestCheckString(unittest.TestCase):  

    def testKnownValues(self):
        minimalmodbus._checkString('DEF', minlength=3, maxlength=3, description='ABC' )
        minimalmodbus._checkString('DEF', minlength=0, maxlength=100, description='ABC' )

    def testTooShort(self):
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DE', minlength=3, maxlength=3, description='ABC')
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DEF', minlength=10, maxlength=3, description='ABC')

    def testTooLong(self):
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DEFG', minlength=1, maxlength=3, description='ABC')
        
    def testInconsistentLengthlimits(self):
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DEFG', minlength=4, maxlength=3, description='ABC')    
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DEF', minlength=-3, maxlength=3, description='ABC') 
        self.assertRaises(ValueError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=-3, description='ABC') 

    def testInputNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkString, None, minlength=3, maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 7, minlength=3, maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 7.0, minlength=3, maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, ['DEF'], minlength=3, maxlength=3, description='ABC')

    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3.0, maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength='GHI', maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=None, maxlength=3, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3.0, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3.0, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength='GHI', description='ABC')

    def testDescriptionNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3, description=12)
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3, description=1.0)
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3, description=None)
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3, description=['ABC'])
        self.assertRaises(TypeError, minimalmodbus._checkString, 'DEF', minlength=3, maxlength=3, description=['A', 'B', 'C'])


class TestCheckInt(unittest.TestCase):  
    
    def testKnownValues(self):
        minimalmodbus._checkInt(47, minvalue=None, maxvalue=None, description='ABC' )
        minimalmodbus._checkInt(47, minvalue=40, maxvalue=50, description='ABC' )
        minimalmodbus._checkInt(47, minvalue=-40, maxvalue=50, description='ABC' )
        minimalmodbus._checkInt(47, description='ABC', maxvalue=50, minvalue=40 )
        minimalmodbus._checkInt(47, minvalue=None, maxvalue=50, description='ABC' )
        minimalmodbus._checkInt(47, minvalue=40, maxvalue=None, description='ABC' )
        
    def testTooLargeValue(self):
        self.assertRaises(ValueError, minimalmodbus._checkInt, 47, minvalue=30, maxvalue=40, description='ABC')
        self.assertRaises(ValueError, minimalmodbus._checkInt, 47, maxvalue=46)
        
    def testTooSmallValue(self):    
        self.assertRaises(ValueError, minimalmodbus._checkInt, 47, minvalue=48 )
        self.assertRaises(ValueError, minimalmodbus._checkInt, 47, minvalue=48, maxvalue=None, description='ABC')
        
    def testInconsistentLimits(self):
        self.assertRaises(ValueError, minimalmodbus._checkInt, 47, minvalue=47, maxvalue=45, description='ABC')         
        
    def testNotIntegerInput(self):
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47.0, minvalue=40)
        self.assertRaises(TypeError, minimalmodbus._checkInt, '47', minvalue=40)
        self.assertRaises(TypeError, minimalmodbus._checkInt, [47], minvalue=40)
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40.0, maxvalue=50, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue='40', maxvalue=50, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=[40], maxvalue=50, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=50.0, description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=[50], description='ABC')
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue='50', description='ABC')
        
    def testDescriptionNotString(self):
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=50, description=12)
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=50, description=1.0)
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=50, description=['A', 'B', 'C'])
        self.assertRaises(TypeError, minimalmodbus._checkInt, 47, minvalue=40, maxvalue=50, description=['ABC'])
        
        
#####################
# Development tools #
#####################

class TestGetDiagnosticString(unittest.TestCase):

    def testReturnsString(self):

        resultstring = minimalmodbus._getDiagnosticString()
        self.assertTrue( len(resultstring) > 100) # For Python 2.6 compatibility


class TestToPrintableStrin(unittest.TestCase):

    def testReturnsPrintable(self):
        allASCII = ''.join( [chr(x) for x in range(256)] )
        
        response = minimalmodbus._toPrintableString(allASCII)
        
        responseCharacterValues = [ord(x) for x in response]
        self.assertTrue( min(responseCharacterValues) > 31 )
        self.assertTrue( max(responseCharacterValues) < 128 )


###########################################
# Communication using a dummy serial port #
###########################################

class TestDummyCommunication(unittest.TestCase):

    ## Test fixture ##

    def setUp(self):   
    
        # Prepare a dummy serial port to have proper responses
        import dummy_serial
        dummy_serial.VERBOSE = False
        dummy_serial.RESPONSES = RESPONSES
        dummy_serial.DEFAULT_RESPONSE = 'NotFoundInDictionary'

        # Monkey-patch a dummy serial port for testing purpose
        minimalmodbus.serial.Serial = dummy_serial.Serial
        
        # Initialize a (dummy) instrument
        self.instrument = minimalmodbus.Instrument('DUMMYPORTNAME', 1) # port name, slave address (in decimal)
        self.instrument._debug = False

    ## Communicate ##

    def testCommunicateNoMessage(self):
        self.assertRaises(ValueError, self.instrument._communicate, '')

    def testCommunicateNoResponse(self):
        self.assertRaises(IOError, self.instrument._communicate, 'MessageForEmptyResponse')

    ## Read bit ##

    def testReadBit(self):      
        self.assertEqual( self.instrument.read_bit(61), 1 )
        self.assertEqual( self.instrument.read_bit(62, functioncode=1), 0 )
    
    def testReadBitWrongAddress(self):
        pass
    
    def testReadBitWrongAddressType(self):
        pass
    def testReadBitWrongFunctioncode(self):
        pass
    
    def testReadBitWrongFunctioncodeType(self):
        pass
                    
    ## Write bit ##
    
    def testWriteBit(self):        
        self.instrument.write_bit(71, 1)
        self.instrument.write_bit(71, 1, 5)
        self.instrument.write_bit(71, 1, functioncode=5)
        self.instrument.write_bit(72, 1, 15)
        self.instrument.write_bit(72, 1, functioncode=15)

    def testWriteBitWrongAddress(self):
        self.assertRaises(ValueError, self.instrument.write_bit, 65536, 1)
        self.assertRaises(ValueError, self.instrument.write_bit, -1, 1)

    def testWriteBitWrongAddressType(self):
        self.assertRaises(TypeError, self.instrument.write_bit, 71.0, 1)
        self.assertRaises(TypeError, self.instrument.write_bit, [71], 1)
        self.assertRaises(TypeError, self.instrument.write_bit, '71', 1)
        self.assertRaises(TypeError, self.instrument.write_bit, None, 1)

    def testWriteBitWrongValue(self):
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 10)
        self.assertRaises(ValueError, self.instrument.write_bit, 71, -5)
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 10, 5)
    
    def testWriteBitWrongValueType(self):
        self.assertRaises(TypeError, self.instrument.write_bit, 71, 1.0)
        self.assertRaises(TypeError, self.instrument.write_bit, 71, [1])
        self.assertRaises(TypeError, self.instrument.write_bit, 71, '1')
        self.assertRaises(TypeError, self.instrument.write_bit, 71, None)
    
    def testWriteBitWrongFunctioncode(self):
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 1, 6)
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 1, -1)
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 1, 0)
        self.assertRaises(ValueError, self.instrument.write_bit, 71, 1, 128)
    
    def testWriteBitWrongFunctioncodeType(self):
        self.assertRaises(TypeError, self.instrument.write_bit, 71, 1, 5.0)
        self.assertRaises(TypeError, self.instrument.write_bit, 71, 1, '5')
        self.assertRaises(TypeError, self.instrument.write_bit, 71, 1, [5])
        self.assertRaises(TypeError, self.instrument.write_bit, 71, 1, None)

    ## Read register ##

    def testReadRegister(self):
        self.assertEqual( self.instrument.read_register(289), 770 )
        self.assertEqual( self.instrument.read_register(5), 184 )
        self.assertEqual( self.instrument.read_register(289, 0), 770 )
        self.assertEqual( self.instrument.read_register(289, 0, 3), 770 ) # functioncode 3
        self.assertEqual( self.instrument.read_register(14, 0, 4), 880 ) # functioncode 4
        
    def testReadRegisterWithDecimals(self):
        self.assertAlmostEqual( self.instrument.read_register(289, 1), 77.0 )
        self.assertAlmostEqual( self.instrument.read_register(289, 2), 7.7  )
        
    def testReadRegisterWrongAddress(self):   
        self.assertRaises(ValueError, self.instrument.read_register, -1) 
        self.assertRaises(ValueError, self.instrument.read_register, 65536) 
        self.assertRaises(ValueError, self.instrument.read_register, -1, 0, 3) 
        
    def testReadRegisterWrongAddressType(self):
        self.assertRaises(TypeError, self.instrument.read_register, 289.0, 0, 3) 
        self.assertRaises(TypeError, self.instrument.read_register, [289], 0, 3) 
        self.assertRaises(TypeError, self.instrument.read_register, '289', 0, 3) 
        self.assertRaises(TypeError, self.instrument.read_register, None, 0, 3) 
        
    def testReadRegisterWithNegativeNumberofdecimals(self):
        self.assertRaises(ValueError, self.instrument.read_register, 289, -1) 
        
    def testReadRegisterNumberofdecimalsNotInteger(self):
        self.assertRaises(TypeError, self.instrument.read_register, 289, 4.0) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, 0.0, 3) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, None) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, '289') 
        
    def testReadRegisterWrongFunctioncode(self):
        self.assertRaises(ValueError, self.instrument.read_register, 289, 0, 5 )
        self.assertRaises(ValueError, self.instrument.read_register, 289, 0, -4 )
        
    def testReadRegisterWrongFunctioncodeType(self):    
        self.assertRaises(TypeError, self.instrument.read_register, 289, 0, 3.0 ) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, 0, [3] ) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, 0, None ) 
        self.assertRaises(TypeError, self.instrument.read_register, 289, 0, '3' ) 
        
    ## Write register ##    
        
    def testWriteRegister(self):    
        self.instrument.write_register(35, 20)    
        self.instrument.write_register(24, 50)    
        self.instrument.write_register(45, 88, functioncode = 6)     
        
    def testWriteRegisterWithDecimals(self):    
        self.instrument.write_register(35, 2.0, 1)    
        self.instrument.write_register(45, 8.8, 1, functioncode = 6)       

    def testWriteRegisterWithWrongValue(self):
        pass
        
        
    def testWriteRegisterWithWrongValueType(self):
        pass
                
        
    def testWriteRegisterWithNegativeNumberofdecimals(self):
        self.assertRaises(ValueError, self.instrument.write_register, 35, 20, -1)     
        
    def testWriteRegisterWithNumberofdecimalsNotInteger(self):     
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, 1.0) 
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, '1') 
        
    def testWriteRegisterWithWrongFunctioncode(self):
        self.assertRaises(ValueError, self.instrument.write_register, 35, 20, functioncode = 12 )    
        self.assertRaises(ValueError, self.instrument.write_register, 35, 20, functioncode = -4 ) 
        
    def testWriteRegisterWithWrongFunctioncodeType(self):    
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, functioncode = '16' ) 
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, functioncode = [16] ) 
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, functioncode = 16.0 ) 
        self.assertRaises(TypeError, self.instrument.write_register, 35, 20, functioncode = None ) 
        
    def testWriteRegisterWithWrongCrcResponse(self):    
        self.assertRaises(ValueError, self.instrument.write_register, 51, 99 ) # Slave gives wrong CRC
        
    def testWriteRegisterWithWrongRegisternumbersResponse(self):     
        self.assertRaises(ValueError, self.instrument.write_register, 52, 99 ) # Slave gives wrong number of registers
            
    def testWriteRegisterWithWrongRegisteraddressResponse(self): 
        self.assertRaises(ValueError, self.instrument.write_register, 53, 99 ) # Slave gives wrong registeraddress
    
    ## Tear down fixture ##
        
    def tearDown(self):
        self.instrument = None
        del(self.instrument)


class TestDummyCommunicationWithPortClosure(unittest.TestCase):

    def setUp(self):   
    
        # Prepare a dummy serial port to have proper responses
        import dummy_serial
        dummy_serial.VERBOSE = False
        dummy_serial.RESPONSES = RESPONSES
        dummy_serial.DEFAULT_RESPONSE = 'NotFoundInDictionary'

        # Monkey-patch a dummy serial port for testing purpose
        minimalmodbus.serial.Serial = dummy_serial.Serial
        
        # Mimic a WindowsXP serial port
        minimalmodbus._CLOSE_PORT_AFTER_EACH_CALL = True

        # Initialize a (dummy) instrument
        self.instrument = minimalmodbus.Instrument('DUMMYPORTNAME', 1) # port name, slave address (in decimal)
        self.instrument._debug = False

    def testReadRegisterSeveralTimes(self):
        self.assertEqual( self.instrument.read_register(289), 770 )
        self.assertEqual( self.instrument.read_register(289), 770 )
        self.assertEqual( self.instrument.read_register(289), 770 )
        
    def testPortAlreadyOpen(self):
        self.assertEqual( self.instrument.read_register(289), 770 )
        self.instrument.serial.open()
        self.assertRaises(IOError, self.instrument.read_register, 289) 
   
    def testPortAlreadyClosed(self):
        self.assertEqual( self.instrument.read_register(289), 770 )
        self.assertRaises(IOError, self.instrument.serial.close) 
 
    def tearDown(self):
        self.instrument = None
        del(self.instrument)

   
class TestVerboseDummyCommunicationWithPortClosure(unittest.TestCase):

    def setUp(self):   
    
        # Prepare a dummy serial port to have proper responses
        import dummy_serial
        dummy_serial.VERBOSE = True
        dummy_serial.RESPONSES = RESPONSES
        dummy_serial.DEFAULT_RESPONSE = 'NotFoundInDictionary'

        # Monkey-patch a dummy serial port for testing purpose
        minimalmodbus.serial.Serial = dummy_serial.Serial
        
        # Mimic a WindowsXP serial port
        minimalmodbus._CLOSE_PORT_AFTER_EACH_CALL = True

        # Initialize a (dummy) instrument
        self.instrument = minimalmodbus.Instrument('DUMMYPORTNAME', 1) # port name, slave address (in decimal)
        self.instrument._debug = False

    def testReadRegister(self):
        self.assertEqual( self.instrument.read_register(289), 770 )   

    def tearDown(self):
        self.instrument = None
        del(self.instrument)


class TestDummyCommunicationDebugmode(unittest.TestCase):

    def setUp(self):   
    
        # Prepare a dummy serial port to have proper responses
        import dummy_serial
        dummy_serial.VERBOSE = False
        dummy_serial.RESPONSES = RESPONSES
        dummy_serial.DEFAULT_RESPONSE = 'NotFoundInDictionary'

        # Monkey-patch a dummy serial port for testing purpose
        minimalmodbus.serial.Serial = dummy_serial.Serial
        
        # Initialize a (dummy) instrument
        self.instrument = minimalmodbus.Instrument('DUMMYPORTNAME', 1) # port name, slave address (in decimal)
        self.instrument._debug = True

    def testReadRegister(self):
        self.assertEqual( self.instrument.read_register(289), 770 )        

    def tearDown(self):
        self.instrument = None
        del(self.instrument)
   
   
RESPONSES = {}
"""A dictionary of respones from a dummy instrument. 

The key is the message (string) sent to the serial port, and the item is the response (string) 
from the dummy serial port.

"""
# Note that the string 'AAAAAAA' might be easier to read if grouped, 
# like 'AA' + 'AAAA' + 'A' for the initial part (address etc) + payload + CRC.

# Read register 289 on slave 1 using function code 3 #
# ---------------------------------------------------#
# Message:  Slave address 1, function code 3. Register address 289, 1 register. CRC. 
# Response: Slave address 1, function code 3. 2 bytes, value=770. CRC=14709.
RESPONSES['\x01\x03' + '\x01!\x00\x01' + '\xd5\xfc'] = '\x01\x03' + '\x02\x03\x02' + '\x39\x75'

# Read register 5 on slave 1 using function code 3 #
# ---------------------------------------------------#
# Message: Slave address 1, function code 3. Register address 289, 1 register. CRC.
# Response: Slave address 1, function code 3. 2 bytes, value=184. CRC
RESPONSES['\x01\x03' + '\x00\x05\x00\x01' + '\x94\x0b'] = '\x01\x03' + '\x02\x00\xb8' + '\xb86'

# Read register 14 on slave 1 using function code 4 #
# --------------------------------------------------#
# Message:  Slave address 1, function code 4. Register address 14, 1 register. CRC. 
# Response: Slave address 1, function code 4. 2 bytes, value=880. CRC.
RESPONSES['\x01\x04' + '\x00\x0e\x00\x01' + 'P\t'] = '\x01\x04' + '\x02\x03\x70' + '\xb8$'

# Write value 50 in register 24 on slave 1 using function code 16 #
# ----------------------------------------------------------------#
# Message:  Slave address 1, function code 16. Register address 24, 1 register, 2 bytes, value=50. CRC. 
# Response: Slave address 1, function code 16. Register address 24, 1 register. CRC.
RESPONSES['\x01\x10' + '\x00\x18\x00\x01\x02\x002' + '$]']       = '\x01\x10' + '\x00\x18\x00\x01' + '\x81\xce'

# Write value 20 in register 35 on slave 1 using function code 16 #
# ----------------------------------------------------------------#
# Message:  Slave address 1, function code 16. Register address 35, 1 register, 2 bytes, value=20. CRC. 
# Response: Slave address 1, function code 16. Register address 35, 1 register. CRC.
RESPONSES['\x01\x10' + '\x00#\x00\x01' + '\x02\x00\x14' + '\xa1\x0c'] = '\x01\x10' + '\x00#\x00\x01' + '\xf0\x03'

# Write value 88 in register 45 on slave 1 using function code 6 #
# ---------------------------------------------------------------#
# Message:  Slave address 1, function code 6. Register address 45, value=88. CRC. 
# Response: Slave address 1, function code 6. Register address 45, value=88. CRC.
RESPONSES['\x01\x06' + '\x00\x2d\x00\x58' + '\x189'] = '\x01\x06' + '\x00\x2d\x00\x58' + '\x189'

# Write value 99 in register 51 on slave 1 using function code 16, slave gives wrong CRC #
# ---------------------------------------------------------------------------------------#
# Message:  Slave address 1, function code 16. Register address 51, 1 register, 2 bytes, value=99. CRC. 
# Response: Slave address 1, function code 16. Register address 51, 1 register. Wrong CRC.
RESPONSES['\x01\x10' + '\x00\x33\x00\x01' + '\x02\x00\x63' + '\xe3\xba'] = '\x01\x10' + '\x00\x33\x00\x01' + 'AB'

# Write value 99 in register 52 on slave 1 using function code 16, slave gives wrong number of registers #
# -------------------------------------------------------------------------------------------------------#
# Message:  Slave address 1, function code 16. Register address 52, 1 register, 2 bytes, value=99. CRC. 
# Response: Slave address 1, function code 16. Register address 52, 2 registers (wrong). CRC.
RESPONSES['\x01\x10' + '\x00\x34\x00\x01' + '\x02\x00\x63' + '\xe2\r'] = '\x01\x10' + '\x00\x34\x00\x02' + '\x00\x06'

# Write value 99 in register 53 on slave 1 using function code 16, slave gives wrong register address #
# ----------------------------------------------------------------------------------------------------#
# Message:  Slave address 1, function code 16. Register address 53, 1 register, 2 bytes, value=99. CRC. 
# Response: Slave address 1, function code 16. Register address 54 (wrong), 1 register. CRC.
RESPONSES['\x01\x10' + '\x00\x35\x00\x01' + '\x02\x00\x63' + '\xe3\xdc'] = '\x01\x10' + '\x00\x36\x00\x01' + '\xe1\xc7'

# Read bit register 61 on slave 1 using function code 2 #   
# ----------------------------------------------------- #
# Message:  Slave address 1, function code 2. Register address 61, 1 coil. CRC. 
# Response: Slave address 1, function code 2. 1 byte, value=1. CRC.
RESPONSES['\x01\x02' + '\x00\x3d\x00\x01' + '(\x06'] = '\x01\x02' + '\x01\x01' + '`H'

# Read bit register 62 on slave 1 using function code 1 #   
# ----------------------------------------------------- #
# Message:  Slave address 1, function code 1. Register address 62, 1 coil. CRC. 
# Response: Slave address 1, function code 1. 1 byte, value=0. CRC.
RESPONSES['\x01\x01' + '\x00\x3e\x00\x01' + '\x9c\x06'] = '\x01\x01' + '\x01\x00' + 'Q\x88'

# Write bit register 71 on slave 1 using function code 5 #   
# ------------------------------------------------------ #
# Message:  Slave address 1, function code 5. Register address 71, value 1 (FF00). CRC. 
# Response: Slave address 1, function code 5. ?????  1 byte, value=1. CRC.
RESPONSES['\x01\x05' + '\x00\x47\xff\x00' + '</'] = '\x01\x05' + '\x00\x47\xff\x00' + '</'

# Write bit register 72 on slave 1 using function code 15 #   
# ------------------------------------------------------ #
# Message:  Slave address 1, function code 15. Register address 72, 1 bit, 1 byte, value 1 (0100). CRC. 
# Response: Slave address 1, function code 15. Register address 72, 1 bit. CRC.
RESPONSES['\x01\x0f' + '\x00\x48\x00\x01\x01\x01' + '\x0fY'] = '\x01\x0f' + '\x00\x48\x00\x01' + '\x14\x1d'

# Retrieve an empty response #
# -------------------------- #
RESPONSES['MessageForEmptyResponse'] = ''

#################
# Run the tests #
#################

if __name__ == '__main__':

    #print hex(61)
    #print repr( minimalmodbus._calculateCrcString( '\x01\x0f' + '\x00\x48\x00\x01' ) )

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestDummyCommunication)
    #unittest.TextTestRunner(verbosity=0).run(suite)

    unittest.main()