/* Testing adding the library path...

*/

// hardware includes
#include "stm32f4xx.h"
#include "LED.h"
#include "Keyboard.h"
#include "misc.h"
#include "stm32f4xx_tim.h"
#include "stm32f4xx_rcc.h"
#include "stm32f4xx_gpio.h"

// monitor includes
#include "residues.h"
#include "formula.h"
#include "circbuf.h"
#include "monitor.h"
#include "monconfig.h"


// 30s minutes of data
#define TDATASIZE	1200

int testdata[TDATASIZE];


// What we'll eventually need:
// moved state to monitor.c
// formulas
// struct	-- list of lists
// taulist	-- resbuf of (step,time) pairs
int delay;
int cstep;	// current step count
int estep, instep;
int lcount;

void fillData() {
	int i;
	for (i = 0; i < TDATASIZE; i++) {
		testdata[i] = 0x00;
		if (i > 400 && i < 600) {
			testdata[i] |= MASK_B;
			if (i < 500) 
				testdata[i] |= MASK_A;
		}
		if ((i % 30) == 0)
			testdata[i] |= MASK_C;
	}
}
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
		RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);

    timerInitStructure.TIM_Prescaler = 42000 - 1;	// get 2kHz clock
    timerInitStructure.TIM_CounterMode = TIM_CounterMode_Up;
    timerInitStructure.TIM_Period = 20 - 1 ;		// 2kHz @ 20 cycles is 10ms
    timerInitStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    timerInitStructure.TIM_RepetitionCounter = 0;
    TIM_TimeBaseInit(TIM3, &timerInitStructure);
    TIM_Cmd(TIM3, ENABLE);
		TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
	
}

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
    nvicStructure.NVIC_IRQChannel = TIM3_IRQn;
    nvicStructure.NVIC_IRQChannelPreemptionPriority = 0;
    nvicStructure.NVIC_IRQChannelSubPriority = 1;
    nvicStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&nvicStructure);
}

//extern "C" 
void TIM2_IRQHandler()
{
    if (TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET)
    {
				// need to copy nstate to cstate and update instep
				///// led stuff to keep track of timing...
				lcount <<= 1;
				if (lcount > 8)
					lcount = 1;
				LED_Out(lcount);
				//////////////////////////////////////////////////
				cstate = nstate;
				instep++;
        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
    }
}

//extern "C" 
void TIM3_IRQHandler()
{
    if (TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET)
    {
			// update nstate somehow
				/*if (instep & 0x20) {
					nstate ^= 0x01;	// alternate A
				}
				if (instep & 0x08) {
					nstate ^= 0x04;
				}*/
				if (instep + 1 < TDATASIZE) 
					nstate = testdata[instep+1];
				else
					nstate = 0;
        TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
    }
}


int main() {
	// local variables
	residue cons_res;
	int cptr, eptr;
	
	// cons variables
	cptr = 0;
	eptr = 0;
	delay = FORM_DELAY;
	// global variable initialization
	instep = 0;
	estep = 0;	
	cstate = 0;
	nstate = 0x02;
	lcount = 1;
	// non-monitor board setup
	LED_Initialize();
	Keyboard_Initialize();
	InitializeTimer();
	EnableTimerInterrupt();
	
	// Fill test data -- let's see what's going on
	fillData();
	
	///////// Start monitor ///////////////////
	// build structure
	build_formula();
	build_struct();
	
	// start the loop
	cstep = 0;
	while (1) {
		// state is updated by interrupts, check if we should be going or not?
		// if the last step we checked (estep) is less than the most recent step 
		// we've received (instep) then run the checker again
		if (estep < instep) {
			// first increment the structure
			incrStruct(estep);
		
			// run conservative
			
			while ((eptr <= cptr) && ((cptr - eptr) >= delay)) {
				cons_res.step = eptr;
				cons_res.form = FORM_NAOBUC;
				reduce(&cons_res);
				if (cons_res.form == FORM_TRUE) {
					// LEDS?
				} else if (cons_res.form == FORM_FALSE) {
					// LEDS?
				} else {	// not possible...
					// LEDS?
				}
				eptr++;
			}
			cptr++;
			
			// run aggressive
		
			// checked current step, increment
			estep++;
		}
	}
}
