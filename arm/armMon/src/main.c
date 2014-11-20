/**
  ******************************************************************************
  * @file    agMon test 3 -- trying to use existing stdperiph project
  * @author  Adapted by Aaron Kane === MCD Application Team 
  * @version V1.0.0
  * @date    19-September-2011
  * @brief   Main program body
  ******************************************************************************
  * @attention
  *
  * THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
  * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
  * TIME. AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY
  * DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
  * FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
  * CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
  *
  * <h2><center>&copy; COPYRIGHT 2011 STMicroelectronics</center></h2>
  ******************************************************************************  
  */ 

//#define USE_FULL_ASSERT

/* Includes ------------------------------------------------------------------*/
#include "stm32f4_discovery.h"
#include "stm32f4xx_tim.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_can.h"
#include "stm32f4xx_rcc.h"
#include "misc.h"

//#include "stm
// Monitor includes
#include "residues.h"
#include "formula.h"
#include "circbuf.h"
#include "monitor.h"
#include "monconfig.h"
#include "gendefs.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
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
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/ 
int delay, cstep, sim = FALSE;
#define TDATASIZE 1200
#define IM_REDUCE
int testdata[TDATASIZE];
CanTxMsg TxMessage;
CanRxMsg RxMessage;
residue cons_res, *cresp;

/* Private function prototypes -----------------------------------------------*/
void Delay (uint32_t nCount);
/* Private functions ---------------------------------------------------------*/



/**
 * CAN Setup function
 */
void InitCAN() {
  GPIO_InitTypeDef  GPIO_InitStructure;
  CAN_InitTypeDef        CAN_InitStructure;
  CAN_FilterInitTypeDef  CAN_FilterInitStructure;
  /* CAN GPIOs configuration **************************************************/

  /* Enable GPIO clock */
  RCC_AHB1PeriphClockCmd(CAN_GPIO_CLK, ENABLE);

  /* Connect CAN pins to AF9 */
  GPIO_PinAFConfig(CAN_GPIO_PORT, CAN_RX_SOURCE, CAN_AF_PORT);
  GPIO_PinAFConfig(CAN_GPIO_PORT, CAN_TX_SOURCE, CAN_AF_PORT); 
  
  /* Configure CAN RX and TX pins */
  GPIO_InitStructure.GPIO_Pin = CAN_RX_PIN | CAN_TX_PIN;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_PuPd  = GPIO_PuPd_UP;
  GPIO_Init(CAN_GPIO_PORT, &GPIO_InitStructure);

  /* CAN configuration ********************************************************/  
  /* Enable CAN clock */
  RCC_APB1PeriphClockCmd(CAN_CLK, ENABLE);
  
  /* CAN register init */
  CAN_DeInit(CANx);

  /* CAN cell init */
  CAN_StructInit(&CAN_InitStructure);
  // Set stuff that isn't default
  /* CAN Baudrate = 1 MBps (CAN clocked at 30 MHz) */
  //CAN_InitStructure.CAN_BS1 = CAN_BS1_6tq;
  //CAN_InitStructure.CAN_BS2 = CAN_BS2_8tq;
  CAN_InitStructure.CAN_BS1 = CAN_BS1_14tq;
  CAN_InitStructure.CAN_BS2 = CAN_BS2_6tq;
  CAN_InitStructure.CAN_Mode = CAN_Mode_Normal;
  //CAN_InitStructure.CAN_Prescaler = 2; // 1Mbps
  CAN_InitStructure.CAN_Prescaler = 4;	// 500kbps
  CAN_Init(CANx, &CAN_InitStructure);

  /* CAN filter init */
#ifdef  USE_CAN1
  CAN_FilterInitStructure.CAN_FilterNumber = 0;
#else /* USE_CAN2 */
  CAN_FilterInitStructure.CAN_FilterNumber = 14;
#endif  /* USE_CAN1 */
  CAN_FilterInitStructure.CAN_FilterMode = CAN_FilterMode_IdMask;
  CAN_FilterInitStructure.CAN_FilterScale = CAN_FilterScale_32bit;
  CAN_FilterInitStructure.CAN_FilterIdHigh = 0x0000;
  CAN_FilterInitStructure.CAN_FilterIdLow = 0x0000;
  CAN_FilterInitStructure.CAN_FilterMaskIdHigh = 0x0000;
  CAN_FilterInitStructure.CAN_FilterMaskIdLow = 0x0000;
  CAN_FilterInitStructure.CAN_FilterFIFOAssignment = 0;
  CAN_FilterInitStructure.CAN_FilterActivation = ENABLE;
  CAN_FilterInit(&CAN_FilterInitStructure);
  
  /* Transmit Structure preparation */

	TxMessage.StdId = 0x01;
  TxMessage.ExtId = 0x01;
  TxMessage.RTR = CAN_RTR_DATA;
  TxMessage.IDE = CAN_ID_STD;
  TxMessage.DLC = 3;
	TxMessage.Data[0] = 0xFF;   // this will get filled with failed invar value
	TxMessage.Data[1] = 0x55;
	TxMessage.Data[2] = 0xAA;
  /* Enable FIFO 0 message pending Interrupt */
  CAN_ITConfig(CANx, CAN_IT_FMP0, ENABLE);
}
/** 
 * Timer Initialization function
 */
void InitializeTimer()
{
  TIM_TimeBaseInitTypeDef timerInitStructure;

	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);

  timerInitStructure.TIM_Prescaler = 42000 - 1;	// get 2kHz clock
  timerInitStructure.TIM_CounterMode = TIM_CounterMode_Up;
  timerInitStructure.TIM_Period = 50 - 1 ;		// 2kHz @ 50 cycles is 25ms
  timerInitStructure.TIM_ClockDivision = TIM_CKD_DIV1;
  timerInitStructure.TIM_RepetitionCounter = 0;
  TIM_TimeBaseInit(TIM2, &timerInitStructure);
  TIM_Cmd(TIM2, ENABLE);
	TIM_ITConfig(TIM2, TIM_IT_Update, ENABLE);
	
		
	// second timer: just for testing to load new values
/*	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);

    timerInitStructure.TIM_Prescaler = 42000 - 1;	// get 2kHz clock
    timerInitStructure.TIM_CounterMode = TIM_CounterMode_Up;
    timerInitStructure.TIM_Period = 20 - 1 ;		// 2kHz @ 20 cycles is 10ms
    timerInitStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    timerInitStructure.TIM_RepetitionCounter = 0;
    TIM_TimeBaseInit(TIM3, &timerInitStructure);
    TIM_Cmd(TIM3, ENABLE);
	TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
	*/	
	
}



/** 
 * Timer and CAN Interrupt Setup function
 */
void EnableTimerInterrupt()
{
    NVIC_InitTypeDef nvicStructure;
    nvicStructure.NVIC_IRQChannel = TIM2_IRQn;
    nvicStructure.NVIC_IRQChannelPreemptionPriority = 1;
    nvicStructure.NVIC_IRQChannelSubPriority = 2;
    nvicStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&nvicStructure);

		// and enable TIM3
		// should be higher urgency (lower "priority" number)
		/*
    nvicStructure.NVIC_IRQChannel = TIM3_IRQn;
    nvicStructure.NVIC_IRQChannelPreemptionPriority = 0;
    nvicStructure.NVIC_IRQChannelSubPriority = 1;
    nvicStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&nvicStructure);
		*/
	
	// Enable CAN
	#ifdef  USE_CAN1 
	nvicStructure.NVIC_IRQChannel = CAN1_RX0_IRQn;
	#else  /* USE_CAN2 */
	nvicStructure.NVIC_IRQChannel = CAN2_RX0_IRQn;
	#endif /* USE_CAN1 */
	nvicStructure.NVIC_IRQChannelPreemptionPriority = 0x0;
	nvicStructure.NVIC_IRQChannelSubPriority = 0x0;
	nvicStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&nvicStructure);
}


//extern "C" 
void TIM2_IRQHandler()
{
    if (TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET || sim)
    {
				int i;
				// safely grab nstate
				// INTERRUPTS OFF
				__disable_irq();
				for (i = 0; i < NPROPINTS; i++) {
					cstate[i] = nstate[i];
				}
        // add any heartbeat style masks here to clear nstate
				__enable_irq();
				// INTERRUPTS ON
				instep++; // this might need to be atomic -- but not used by anyone above us
				incrStruct(instep);
				// add residue to list
				for (i = 0; i < NPOLICIES; i++) {
					cons_res.step = instep;
					cons_res.form = POLICIES[i];

					// reduce when we add
					#ifdef IM_REDUCE 
					reduce(instep, &cons_res,0);
					#endif
					rbInsert(&mainresbuf[i], cons_res.step, cons_res.form);
					// this should be ok here (don't need to do all inserts before checking 
					checkConsStep(&mainresbuf[i], i);
				}

				// just to see that we're running...
				if ((instep % 40) == 0) { // 1s (40@25ms)
						STM_EVAL_LEDToggle(LED3);
				}
				//CAN_Transmit(CANx, &TxMessage);
        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
    }
}

//extern "C" 
void TIM3_IRQHandler()
{
    if (TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET || sim)
    {
				if (instep + 1 < TDATASIZE) 
					nstate[0] = testdata[instep+1];
				else
					nstate[0] = 0;
        TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
    }
}

// quick define, we'll put these into maskdefs once we know what they are
#define MASK_HB 1
// Fill nstate with current CAN value -- 
// this should actually come from genmonconfig eventually
void updateState() {
		switch (RxMessage.StdId) {
      // fill 'em up
      case NET_HB:
        nstate[0] |= ((RxMessage.Data[0] & (1 << 4)) << MASK_HB); // or whatever
        break;
			// fake value fill for now
			case 0x1A0:
				nstate[0] = RxMessage.Data[0];
				break;
			//case 0x1A1:
			//		nstate[1] = RxMessage.Data[0];
			//	break;
			case 0x555:
				nstate[1] = 0;
				if (RxMessage.Data[0] > 10)
						nstate[0] |= 0x01;
				break;
		}
}
int checkReceive(CanRxMsg *msg) {
	if ((msg->DLC != 3) || msg->StdId != 0x321) {
		return 0;
	}
	if ((msg->Data[0] | (msg->Data[1] << 8) | (msg->Data[2] << 16)) != 0xAA55AA) {
		return -1;
	}
	return 1;
}
//extern "C"
void CAN1_RX0_IRQHandler() {
	if (CAN_GetITStatus(CANx, CAN_IT_FMP0) == SET) {
		CAN_Receive(CANx, CAN_FIFO0, &RxMessage);
	}
	updateState();
}
/**
  * @brief   Main program
  * @param  None
  * @retval None
  */
int main(void)
{
	residue res, *resp;
	int start, end, i;
	int agstep;
	delay = FORM_DELAY;
	// global variable initialization
	instep = 0;
	estep = 0;	
	//cstate[0] = 0;
	//nstate[0] = 0x00;
	for (i = 0; i < NPROPINTS; i++) {
		cstate[i] = 0;
		nstate[i] = 0;
	}

	
	for (i = 0; i < TDATASIZE; i++) {
		testdata[i] = 0x01;
	}
	
	//// non-monitor setup
	InitCAN();
	InitializeTimer();
	//// Timer interrupt starts the monitor, call EnableTimerInterrupt() below when ready
	
  /* Initialize LEDs mounted on STM32F4-Discovery board ***************************/
  STM_EVAL_LEDInit(LED4);
  STM_EVAL_LEDInit(LED3);
  STM_EVAL_LEDInit(LED5);
  STM_EVAL_LEDInit(LED6);
  
  /* Turn on LED4 and LED5 */
  //STM_EVAL_LEDOn(LED4);
  //STM_EVAL_LEDOn(LED5);
  

///////// Start monitor ///////////////////
	// build structure
	build_formula();
	build_struct();
	
	// start the loop
	cstep = 0;
	// start CAN and monitor
	EnableTimerInterrupt();
	// Conservative check is done in timer interrupt
	// So main loop is just constant aggressive check 
	// and waiting if we happen to finish
	while (1) {
		// can't simulator timer interrupts, just call them instead...
		if (sim) {
			TIM3_IRQHandler();
			TIM2_IRQHandler();
			/*	while (CAN_MessagePending(CANx, CAN_FIFO0) < 1) {
				// wait...
			};*/
			CAN1_RX0_IRQHandler();
			checkReceive(&RxMessage);
		}
		// run aggressive monitor
		// need to be aware of state updating out from under us
		// but it's always safe to give the "old" answer and then keep going
		// grab state
		for (i = 0; i < NPOLICIES; i++) {
			NVIC_DisableIRQ(TIM2_IRQn);
			agstep = instep;
			start = mainresbuf[i].start;
			end = mainresbuf[i].end;
			NVIC_EnableIRQ(TIM2_IRQn);
			while (start != end) {
				///////////////////////////////////
				// just disable the conservative trigger
				NVIC_DisableIRQ(TIM2_IRQn);
				resp = rbGet(&mainresbuf[i], start);
				// copy residue
				res.form = resp->form;
				res.step = resp->step;
				NVIC_EnableIRQ(TIM2_IRQn);
				////////////////////////////////////
				// now we can reduce our copied residue
				reduce(instep, &res, 1);
				// check for aggressive violation
				if (res.form == FORM_FALSE) {
					// we're triggering this failure without ensuring it'll get into the buffer for now
					// need to see how much jitter all this blocking will add
					traceViolate(i);
				}
				////////////////////////////////
				// check if we got interrupted by period
				NVIC_DisableIRQ(TIM2_IRQn);
				if (agstep == instep) {
					// put res into mainresbuf[start]
					mainresbuf[i].buf[start].form = res.form;
					mainresbuf[i].buf[start].step = res.step;
					start = (start + 1) % mainresbuf[i].size;
				} else {
					start = mainresbuf[i].start;
					end = mainresbuf[i].end;
					agstep = instep;
				}
				NVIC_EnableIRQ(TIM2_IRQn);
				//////////////////////////////
			}
		}
		// checked everything, busy wait until next tick
		// ok to not lock here, we might miss by one iteration
		// but that should be better than constantly locking
		while (agstep == instep) {}
	}
}

/** Trace satisfaction and violation -- what to do when these happens depends on system, so putting here */
void traceViolate(int i) {
	STM_EVAL_LEDOff(LED4);
	STM_EVAL_LEDOn(LED5);
  // send Violation message
  TxMessage.Data[0] = i;
	CAN_Transmit(CANx, &TxMessage);
}
void stepSatisfy() {
	STM_EVAL_LEDOn(LED4);
}
void traceFail() {
	STM_EVAL_LEDOn(LED6);
}

/**
  * @brief  Inserts a delay time.
  * @param  nCount: specifies the delay time length.
  * @retval None
  */
void Delay(__IO uint32_t nCount)
{
  /* Decrement nCount value */
  while (nCount != 0)
  {
    nCount--;
  }
}

#ifdef  USE_FULL_ASSERT

/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif
 


/******************* (C) COPYRIGHT 2011 STMicroelectronics *****END OF FILE****/



 // Old main code -- 
//  while (1) {
//		// can't simulator timer interrupts, just call them instead...
//		if (sim) {
//			TIM3_IRQHandler();
//			TIM2_IRQHandler();
//			/*	while (CAN_MessagePending(CANx, CAN_FIFO0) < 1) {
//				// wait...
//			};*/
//			CAN1_RX0_IRQHandler();
//			checkReceive(&RxMessage);
//		}
//		// state is updated by interrupts, check if we should be going or not?
//		// if the last step we checked (estep) is less than the most recent step 
//		// we've received (instep) then run the checker again
//		//@TODO -- need to grab instep so it doesn't get changed out from under us here
//		if (estep < instep) {
//			// first increment the structure
//			incrStruct(estep);
//		
//			// run conservative
//			cons_res.step = estep;
//			cons_res.form = POLICY;
//			reduce(instep, &cons_res);
//			rbInsert(&mainresbuf, cons_res.step, cons_res.form);
//			
//			start = mainresbuf.start;
//			end = mainresbuf.end;
//			while (start != end) {
//				resp = rbGet(&mainresbuf, start);
//				//cons_res = *(rbGet(&mainresbuf, start));
//				if ((estep - resp->step) >= delay) {
//					reduce(estep, resp);
//					if (resp->form == FORM_TRUE) {
//						// LEDS?
//					} else if (resp->form == FORM_FALSE) {
//						// LEDS?
//					} else {	// not possible...
//						// LEDS?
//					}
//				} else {
//					// mainresbuf is ordered, later residues can't be from earlier
//					break;
//				}
//				start = (start + 1) % mainresbuf.size;
//			}
//			// run aggressive
//		
//			// checked current step, increment
//			estep++;
//		}
//	}
