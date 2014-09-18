// monitor includes
#include "residues.h"
#include "formula.h"
#include "circbuf.h"
#include "monitor.h"
#include "monconfig.h"


// pc includes
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

#define NFIELDS 6
// csv stuff
char buf[200];		/* input line buffer */
char field[NFIELDS];	/* fields */
//long long timeus;
unsigned long timeus;
unsigned long mytimer;
double mtimeus = 0;
int stepcount = 0;

// OSX clock stuff
#ifdef __MACH__
clock_serv_t cclock;
mach_timespec_t mts;
#endif

// Use clock_gettime in linux, clock_get_time in OS X.
void get_monotonic_time(struct timespec *ts){
#ifdef __MACH__
  clock_get_time(cclock, &mts);
  ts->tv_sec = mts.tv_sec;
  ts->tv_nsec = mts.tv_nsec;
#else
  clock_gettime(CLOCK_MONOTONIC, ts);
#endif
}
double get_elapsed_time(struct timespec *before, struct timespec *after){
  double deltat_s  = after->tv_sec - before->tv_sec;
  double deltat_ns = after->tv_nsec - before->tv_nsec;
  return deltat_s + deltat_ns*1e-9;
}

//stolen from 'the practice of programming'
int csvgetline(FILE *fin)
{	
	int nfield;
	char *p, *q;
	/* spacer */
	if (fgets(buf, sizeof(buf), fin) == NULL) {
		return -1;
	}
	nfield = 0;
	for (q = buf; (p=strtok(q, ",\n\r")) != NULL; q = NULL)
		field[nfield++] = (*p == '0' ? 0 : 1);
	return nfield;
}


int sim = TRUE;
// monitor vars
int delay;	
int cstep;	// current step count
int lcount;
int tracesat;


int main(int argc, char** argv) {
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
	//fillData2();
	#ifdef __MACH__
  	host_get_clock_service(mach_host_self(), SYSTEM_CLOCK, &cclock);
	#endif
	
	struct timeval ts, te;
	struct timespec tsm, tem;
	timeus = 0;
	mytimer = 0;
	// keep track of violated or not
	tracesat = 1;
	FILE *infile;
	infile = fopen(argv[1], "r");
	///////// Start monitor ///////////////////
	// build structure
	build_formula();
	build_struct();
	
	printf("got to the loop...\n\r");
	// start the loop
	cstep = 0;
	int traceFinished = 0;
	// read the csv header
	if (fgets(buf, sizeof(buf), infile) == NULL) {
		printf("csv needs a header line!");
		exit(1);
	}
	printf("read header line\n");
	printf("%s", buf);
	// was while(1)
	while ((traceFinished = csvgetline(infile)) != -1) {
		gettimeofday(&ts, NULL);
		get_monotonic_time(&tsm);
		// fill cstate
		cstate = 0;
		int i;
		// start at 1 to skip time field
		for (i = 1; i < NFIELDS; i++) { 
			cstate |= (field[i] << i);
		}
		instep++;
		//printf("checking props: x: %d, p: %d, q: %d, r: %d, t: %d\n", getProp(MASK_x), getProp(MASK_p), getProp(MASK_q), getProp(MASK_r), getProp(MASK_t));
		
		// state is updated by interrupts, check if we should be going or not?
		// if the last step we checked (estep) is less than the most recent step 
		// we've received (instep) then run the checker again
		//@TODO -- need to grab instep so it doesn't get changed out from under us here
		if (estep <= instep) {
			// first increment the structure
			incrStruct(estep);
		
			// run conservative
			cons_res.step = estep;
			cons_res.form = POLICY;
			//printf("before reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			reduce(instep, &cons_res);
			//printf("after reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			rbInsert(&mainresbuf, cons_res.step, cons_res.form);
			//printf("added (%d,%d) to ring\n", cons_res.step, cons_res.form);
			
			start = mainresbuf.start;
			end = mainresbuf.end;
			while (start != end) {
				resp = rbGet(&mainresbuf, start);
				if ((estep - resp->step) >= delay) {
					reduce(estep, resp);
					//printf("estep: %d, rstep: %d, form: %d\n", estep, resp->step, resp->form);
					if (resp->form == FORM_TRUE) {
						//printf("step %d is TRUE\n", resp->step);
						//rbRemoveFirst(&mainresbuf);
					} else if (resp->form == FORM_FALSE) {
						//printf("step %d is FALSE\n", resp->step);
						//rbRemoveFirst(&mainresbuf);
						tracesat = 0;
						// LEDS?
					} else {	// not possible...
						printf("%d@@step %d is ELSE? -- %d\n", estep, resp->step, resp->form);
						// LEDS?
					}
				} else {
					// mainresbuf is ordered, later residues can't be from earlier
				//	break;
				}
				start = (start + 1) % mainresbuf.size;
			}
			// run aggressive
		
			// checked current step, increment
			estep++;
		}
		//printf("getting timeofday, timeus is %lu\n", timeus);
		gettimeofday(&te, NULL);
		get_monotonic_time(&tem);
		//long long add = (te.tv_sec - ts.tv_sec) * 1000000;
		unsigned int add; double addm;
		//timeus += (te.tv_sec - ts.tv_sec) * 1000000;
		//printf("added secs: timeus is %lld\n", timeus);
		//timeus += (te.tv_usec - ts.tv_usec);
		add = (te.tv_usec - ts.tv_usec);
		addm = get_elapsed_time(&tsm, &tem);
		stepcount = stepcount + 1;
		printf("loop time is %d, mach time is %f, mtotal: %f step: %d\n", add, addm, mtimeus, stepcount);
		mtimeus = mtimeus + addm;
		/*printf("timeus is %lu before add\n", timeus);
		timeus = timeus + add;
		printf("timeus is %lu after add\n",timeus);
		printf("adding %d to timeus\n", add);
		printf("added usecs: timeus is %lu\n", timeus);
		*/
	}
	printf("elapsed time to check is %d, mach time is %f, at %d steps\n", timeus, mtimeus, stepcount);
	printf("finished loop\n");
	printf("Trace finished. Satisfied is %s\n", tracesat ? "true" : "false");
	#ifdef __MACH__
  	mach_port_deallocate(mach_task_self(), cclock);
	#endif

}
