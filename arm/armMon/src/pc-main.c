// monitor includes
#include "residues.h"
#include "formula.h"
#include "circbuf.h"
#include "monitor.h"
#include "monconfig.h"
#include "gendefs.h"


// pc includes
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

#ifndef MON_TYPE
#define MON_CONS
#define MON_AGGR
#endif

#define NFIELDS 100
// csv stuff
char buf[2048];		/* input line buffer */
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
	for (q = buf; (p=strtok(q, ",\n\r")) != NULL; q = NULL) {
		if (strcmp(p,"0") != 0) {
			field[nfield] = 1;
		} else {
			field[nfield] = 0;
		}
		nfield++;
	}
	return nfield;
}

void updateState() {
	// start at 1 to skip time field
	//	cstate |= field[0];
	cstate |= field[1] << 1;
	cstate |= field[2] << 2;
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
	delay = FORM_DELAY;
	// global variable initialization
	instep = 0;
	estep = 0;	
	cstate = 0;
	nstate = 0x02;
	lcount = 1;
	
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
	while ((traceFinished = csvgetline(infile)) > 0) {
		gettimeofday(&ts, NULL);
		get_monotonic_time(&tsm);
		// fill cstate
		cstate = 0;
		int i;
		////// FILL STATE
		updateState();
		////////////////
		instep = instep + 1;
		
		// first increment the structure
		incrStruct(estep);
		// add residue to list
	
		// if we've received a new state (instep) that we haven't checked (estep), check
		//if (estep <= instep) {
		
			// add residue to list
			cons_res.step = instep;
			cons_res.form = POLICY;
			//printf("before reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			#ifdef IM_REDUCE
			reduce(instep, &cons_res);
			#endif
			//printf("after reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			rbInsert(&mainresbuf, cons_res.step, cons_res.form);
			//printf("added (%d,%d) to ring\n", cons_res.step, cons_res.form);
			#ifdef MON_CONS
			checkConsStep();
			#endif
		
			#ifdef MON_AGGR
			//////// START AGGRESSIVE CHECK //////////////
			////////////////////////////////////////////
			start = mainresbuf.start;
			end = mainresbuf.end;
			printf("start %d, end %d", start, end);
			while (start != end) {
				resp = rbGet(&mainresbuf, start);
				reduce(instep, resp);
				printf("in step: %d, reduced %d to %d\n", instep, resp->step, resp->form);
				//printf("estep: %d, rstep: %d, form: %d\n", estep, resp->step, resp->form);
				if (resp->form == FORM_TRUE) {
					//printf("step %d is TRUE\n", resp->step);
					//rbRemoveFirst(&mainresbuf);
					rbSafeRemove(&mainresbuf, start);
					stepSatisfy();
				} else if (resp->form == FORM_FALSE) {
					//printf("step %d is FALSE\n", resp->step);
					rbSafeRemove(&mainresbuf, start);
					traceViolate();
					// LEDS?
				} 
				/*else {	// not possible...
					printf("%d@@step %d is ELSE? -- %d\n", instep, resp->step, resp->form);
					exit(-1);
					// LEDS?
				}*/
				start = (start + 1) % mainresbuf.size;
			}
			#endif
			/////////////// END AGGRESSIVE CHECK ////////////////////
			/////////////////////////////////////////////////////////
		//}
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
	////////////////////////////////////////////////
	// FINISHED CHECKING, print stats
	printf("elapsed time to check is %d, mach time is %f, at %d steps\n", timeus, mtimeus, stepcount);
	printf("finished loop\n");
	printf("Trace finished. Satisfied is %s\n", tracesat ? "true" : "false");
	#ifdef __MACH__
  	mach_port_deallocate(mach_task_self(), cclock);
	#endif
} // END MAIN



void traceViolate() {
	//printf("Trace VIOLATED!!!\n");
	tracesat = 0;
}
void stepSatisfy() {
	// do nothing...	
}
void traceFail() {
	printf("FAILED REDUCE\n");
	exit(-2);
}
