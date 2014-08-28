/* Testing adding the library path...

*/

// hardware includes
/*
#include "stm32f4xx.h"
#include "LED.h"
#include "Keyboard.h"
#include "misc.h"
#include "stm32f4xx_tim.h"
#include "stm32f4xx_rcc.h"
#include "stm32f4xx_gpio.h"
*/
// monitor includes
#include "residues.h"
#include "formula.h"
#include "circbuf.h"
#include "monitor.h"
#include "monconfig.h"


///////////////// CANDEF
#define USE_CAN1
//#define USE_CAN2 

#ifdef  USE_CAN1
  #define CANx                       CAN1
  #define CAN_CLK                    RCC_APB1Periph_CAN1
  #define CAN_RX_PIN                 GPIO_Pin_0
  #define CAN_TX_PIN                 GPIO_Pin_1
  #define CAN_GPIO_PORT              GPIOD
  #define CAN_GPIO_CLK               RCC_AHB1Periph_GPIOD
  #define CAN_AF_PORT                GPIO_AF_CAN1
  #define CAN_RX_SOURCE              GPIO_PinSource0
  #define CAN_TX_SOURCE              GPIO_PinSource1       
#else /*USE_CAN2*/
  #define CANx                       CAN2
  #define CAN_CLK                    (RCC_APB1Periph_CAN1 | RCC_APB1Periph_CAN2)
  #define CAN_RX_PIN                 GPIO_Pin_5
  #define CAN_TX_PIN                 GPIO_Pin_13
  #define CAN_GPIO_PORT              GPIOB
  #define CAN_GPIO_CLK               RCC_AHB1Periph_GPIOB
  #define CAN_AF_PORT                GPIO_AF_CAN2
  #define CAN_RX_SOURCE              GPIO_PinSource5
  #define CAN_TX_SOURCE              GPIO_PinSource13    
#endif  /* USE_CAN1 */
///////////////////////////


// 30s minutes of data
#define TDATASIZE	1200

int testdata[TDATASIZE];
int sim = TRUE;

// What we'll eventually need:
// moved state to monitor.c
// formulas
// struct	-- list of lists
// taulist	-- resbuf of (step,time) pairs
int delay;	
int cstep;	// current step count
int lcount;

void fillData() {
	int i;
	for (i = 0; i < TDATASIZE; i++) {
		testdata[i] = 0x00;
		if (i > 400 && i < 600) {
			testdata[i] |= MASK_b;
			if (i < 500) 
				testdata[i] |= MASK_a;
		}
		if ((i % 30) == 0)
			testdata[i] |= MASK_c;
	}
}



//@@void InitCAN() {
//@@  GPIO_InitTypeDef  GPIO_InitStructure;
//@@  CAN_InitTypeDef        CAN_InitStructure;
//@@	CAN_FilterInitTypeDef  CAN_FilterInitStructure;
//@@	CanTxMsg TxMessage;
//@@  /* CAN GPIOs configuration **************************************************/
//@@
//@@  /* Enable GPIO clock */
//@@  RCC_AHB1PeriphClockCmd(CAN_GPIO_CLK, ENABLE);
//@@
//@@  /* Connect CAN pins to AF9 */
//@@  GPIO_PinAFConfig(CAN_GPIO_PORT, CAN_RX_SOURCE, CAN_AF_PORT);
//@@  GPIO_PinAFConfig(CAN_GPIO_PORT, CAN_TX_SOURCE, CAN_AF_PORT); 
//@@  
//@@  /* Configure CAN RX and TX pins */
//@@  GPIO_InitStructure.GPIO_Pin = CAN_RX_PIN | CAN_TX_PIN;
//@@  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
//@@  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
//@@  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
//@@  GPIO_InitStructure.GPIO_PuPd  = GPIO_PuPd_UP;
//@@  GPIO_Init(CAN_GPIO_PORT, &GPIO_InitStructure);
//@@
//@@  /* CAN configuration ********************************************************/  
//@@  /* Enable CAN clock */
//@@  RCC_APB1PeriphClockCmd(CAN_CLK, ENABLE);
//@@  
//@@  /* CAN register init */
//@@  CAN_DeInit(CANx);
//@@
//@@  /* CAN cell init */
//@@  CAN_StructInit(&CAN_InitStructure);
//@@	// Set stuff that isn't default
//@@  /* CAN Baudrate = 1 MBps (CAN clocked at 30 MHz) */
//@@  CAN_InitStructure.CAN_BS1 = CAN_BS1_6tq;
//@@  CAN_InitStructure.CAN_BS2 = CAN_BS2_8tq;
//@@  CAN_InitStructure.CAN_Prescaler = 2;
//@@  CAN_Init(CANx, &CAN_InitStructure);
//@@
//@@  /* CAN filter init */
//@@#ifdef  USE_CAN1
//@@  CAN_FilterInitStructure.CAN_FilterNumber = 0;
//@@#else /* USE_CAN2 */
//@@  CAN_FilterInitStructure.CAN_FilterNumber = 14;
//@@#endif  /* USE_CAN1 */
//@@  CAN_FilterInitStructure.CAN_FilterMode = CAN_FilterMode_IdMask;
//@@  CAN_FilterInitStructure.CAN_FilterScale = CAN_FilterScale_32bit;
//@@  CAN_FilterInitStructure.CAN_FilterIdHigh = 0x0000;
//@@  CAN_FilterInitStructure.CAN_FilterIdLow = 0x0000;
//@@  CAN_FilterInitStructure.CAN_FilterMaskIdHigh = 0x0000;
//@@  CAN_FilterInitStructure.CAN_FilterMaskIdLow = 0x0000;
//@@  CAN_FilterInitStructure.CAN_FilterFIFOAssignment = 0;
//@@  CAN_FilterInitStructure.CAN_FilterActivation = ENABLE;
//@@  CAN_FilterInit(&CAN_FilterInitStructure);
//@@  
//@@  /* Transmit Structure preparation */
//@@  TxMessage.StdId = 0x321;
//@@  TxMessage.ExtId = 0x01;
//@@  TxMessage.RTR = CAN_RTR_DATA;
//@@  TxMessage.IDE = CAN_ID_STD;
//@@  TxMessage.DLC = 1;
//@@  
//@@  /* Enable FIFO 0 message pending Interrupt */
//@@  CAN_ITConfig(CANx, CAN_IT_FMP0, ENABLE);
//@@}

void fillData2() {
	int i;
	testdata[0] = 0x00;
	testdata[1] = 0x00;
	testdata[2] = 0x00;
	testdata[3] |= MASK_a | MASK_b;
	testdata[4] |= MASK_b;
	testdata[5] |= MASK_b;
	testdata[6] |= MASK_b;
	testdata[7] |= MASK_b;
	testdata[8] |= MASK_b | MASK_c;
	testdata[9] |= 0;//MASK_B;
	testdata[10] |= MASK_c;
	for (i = 11; i < 200; i++) {
		testdata[i] = 0x00;
	}
	
}
//@@void InitializeTimer()
//@@{
//@@    TIM_TimeBaseInitTypeDef timerInitStructure;
//@@
//@@		RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
//@@
//@@    timerInitStructure.TIM_Prescaler = 42000 - 1;	// get 2kHz clock
//@@    timerInitStructure.TIM_CounterMode = TIM_CounterMode_Up;
//@@    timerInitStructure.TIM_Period = 50 - 1 ;		// 2kHz @ 50 cycles is 25ms
//@@    timerInitStructure.TIM_ClockDivision = TIM_CKD_DIV1;
//@@    timerInitStructure.TIM_RepetitionCounter = 0;
//@@    TIM_TimeBaseInit(TIM2, &timerInitStructure);
//@@    TIM_Cmd(TIM2, ENABLE);
//@@		TIM_ITConfig(TIM2, TIM_IT_Update, ENABLE);
//@@	
//@@		
//@@		// second timer: just for testing to load new values
//@@		RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);
//@@
//@@    timerInitStructure.TIM_Prescaler = 42000 - 1;	// get 2kHz clock
//@@    timerInitStructure.TIM_CounterMode = TIM_CounterMode_Up;
//@@    timerInitStructure.TIM_Period = 20 - 1 ;		// 2kHz @ 20 cycles is 10ms
//@@    timerInitStructure.TIM_ClockDivision = TIM_CKD_DIV1;
//@@    timerInitStructure.TIM_RepetitionCounter = 0;
//@@    TIM_TimeBaseInit(TIM3, &timerInitStructure);
//@@    TIM_Cmd(TIM3, ENABLE);
//@@		TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
//@@		
//@@	
//@@}
//@@
//@@void EnableTimerInterrupt()
//@@{
//@@    NVIC_InitTypeDef nvicStructure;
//@@    nvicStructure.NVIC_IRQChannel = TIM2_IRQn;
//@@    nvicStructure.NVIC_IRQChannelPreemptionPriority = 1;
//@@    nvicStructure.NVIC_IRQChannelSubPriority = 2;
//@@    nvicStructure.NVIC_IRQChannelCmd = ENABLE;
//@@    NVIC_Init(&nvicStructure);
//@@
//@@		// and enable TIM3
//@@		// should be higher urgency (lower "priority" number)
//@@    nvicStructure.NVIC_IRQChannel = TIM3_IRQn;
//@@    nvicStructure.NVIC_IRQChannelPreemptionPriority = 0;
//@@    nvicStructure.NVIC_IRQChannelSubPriority = 1;
//@@    nvicStructure.NVIC_IRQChannelCmd = ENABLE;
//@@    NVIC_Init(&nvicStructure);
//@@	
//@@	// Enable CAN
//@@	#ifdef  USE_CAN1 
//@@	nvicStructure.NVIC_IRQChannel = CAN1_RX0_IRQn;
//@@	#else  /* USE_CAN2 */
//@@	nvicStructure.NVIC_IRQChannel = CAN2_RX0_IRQn;
//@@	#endif /* USE_CAN1 */
//@@  nvicStructure.NVIC_IRQChannelPreemptionPriority = 0x0;
//@@  nvicStructure.NVIC_IRQChannelSubPriority = 0x0;
//@@  nvicStructure.NVIC_IRQChannelCmd = ENABLE;
//@@  NVIC_Init(&nvicStructure);
//@@}


//extern "C" 
void TIM2_IRQHandler()
{
//@@    if (TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET || sim)
    if (sim)
    {
				cstate = nstate;
				instep++;
//@@        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
    }
}

//extern "C" 
void TIM3_IRQHandler()
{
//@@    if (TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET || sim)
    if (sim)
    {
				if (instep + 1 < TDATASIZE) 
					nstate = testdata[instep+1];
				else
					nstate = 0;
//@@        TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
    }
}
//extern "C"
void CAN1_RX0_IRQHandler() {
	// might not need to check flags, need to look around a bit more
	/*if (CAN_GetITStatus(CANx, CAN_IT_FMP0) == SET) {
		
	} else if (CAN_GetITStatus(CANx, CAN_IT_FMP1) == SET) {
		
	}*/
}

int main() {
	// local variables
	residue cons_res;
	residue* resp;
	//int cptr, eptr;
	int start, end;
	// cons variables
	//cptr = 0;
	//eptr = 0;
	delay = FORM_DELAY;
	// global variable initialization
	instep = 0;
	estep = 0;	
	cstate = 0;
	nstate = 0x02;
	lcount = 1;
	// non-monitor board setup
//@@	LED_Initialize();
//@@	Keyboard_Initialize();
//@@	InitializeTimer();
//@@	EnableTimerInterrupt();
	
	// Fill test data -- let's see what's going on
	//fillData();
	fillData2();
	
	///////// Start monitor ///////////////////
	// build structure
	build_formula();
	build_struct();
	
	// start the loop
	cstep = 0;
	while (1) {
		// can't simulator timer interrupts, just call them instead...
		if (sim) {
			TIM3_IRQHandler();
			TIM2_IRQHandler();
		}
		// state is updated by interrupts, check if we should be going or not?
		// if the last step we checked (estep) is less than the most recent step 
		// we've received (instep) then run the checker again
		//@TODO -- need to grab instep so it doesn't get changed out from under us here
		if (estep < instep) {
			// first increment the structure
			incrStruct(estep);
		
			// run conservative
			cons_res.step = estep;
			cons_res.form = POLICY;
			reduce(instep, &cons_res);
			rbInsert(&mainresbuf, cons_res.step, cons_res.form);
			
			start = mainresbuf.start;
			end = mainresbuf.end;
			while (start != end) {
				resp = rbGet(&mainresbuf, start);
				//cons_res = *(rbGet(&mainresbuf, start));
				if ((estep - resp->step) >= delay) {
					reduce(estep, resp);
					if (resp->form == FORM_TRUE) {
						// LEDS?
					} else if (resp->form == FORM_FALSE) {
						// LEDS?
					} else {	// not possible...
						// LEDS?
					}
				} else {
					// mainresbuf is ordered, later residues can't be from earlier
					break;
				}
				start = (start + 1) % mainresbuf.size;
			}
			// run aggressive
		
			// checked current step, increment
			estep++;
		}
	}
}
