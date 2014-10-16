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

/*#ifndef MON_TYPE
#define MON_CONS
#define MON_AGGR
#endif
*/
#define IM_REDUCE

#define NFIELDS 100
// csv stuff
char buf[2048];		/* input line buffer */
char field[NFIELDS];	/* fields */
//long long timeus;
unsigned long timeus;
unsigned long mytimer;
unsigned long stepcount = 0;
unsigned long nt_incr = 0, nt_polinc=0, nt_cons=0, nt_aggr=0;
unsigned long lmtime = 0;

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

unsigned long get_elapsed_ltime(struct timespec *before, struct timespec *after) {
	return (after->tv_sec - before->tv_sec)*1000000000 + (after->tv_nsec-before->tv_nsec);
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
	cstate |= field[3] << 3;
	cstate |= field[4] << 4;
	cstate |= field[5] << 5;
	cstate |= field[6] << 6;
	cstate |= field[7] << 7;
	cstate |= field[8] << 8;
	cstate |= field[9] << 9;
	cstate |= field[10] << 10;
	cstate |= field[11] << 11;
	cstate |= field[12] << 12;
	cstate |= field[13] << 13;
	cstate |= field[14] << 14;
	cstate |= field[15] << 15;

	//printf("allT: %d, allF: %d, alt1: %d, perF3: %d\n", getProp(MASK_allT), getProp(MASK_allF), getProp(MASK_alt1), getProp(MASK_perF3));
	instep++;
	//printf("cstate is %x @ %d\n", cstate, instep);
}

int sim = TRUE;
// monitor vars
int delay;	
int cstep;	// current step count
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
	nstate = 0;	// don't use it, but better to leave it initialized
	
	// keep track of violated or not
	tracesat = 1;

	/////////////////
	///// profiling stuff
	#ifdef __MACH__
  	host_get_clock_service(mach_host_self(), SYSTEM_CLOCK, &cclock);
	#endif
	// set numreduces for profiling
	numreduces=0;
	// timing vars
	struct timespec tsm, tem, total_tsm, total_tem;
	timeus = 0;
	mytimer = 0;
	nt_incr = 0;
	// ////////////////
	// input file
	FILE *infile;
	infile = fopen(argv[1], "r");
	/////////////////////////////////////////////
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
	printf("Checking trace...\n");
	// was while(1)
	// get entire time to finish
	get_monotonic_time(&total_tsm);
	while ((traceFinished = csvgetline(infile)) > 0) {
		//get_monotonic_time(&tsm);
		//numreduces = 0;
		
		// fill cstate
		/////////////////////////////////////////
		////// FILL STATE
		cstate = 0;
		updateState();	// updates instep now
		////////////////
		


		///////////////////////////////////////////////
		////////// INCREMENT STRUCTURE
		// first increment the structure
		get_monotonic_time(&tsm);
		incrStruct(instep);
		get_monotonic_time(&tem);
		nt_incr += get_elapsed_ltime(&tsm, &tem);
		/////////////////////////////////////////////////////
	



		/////////////////////////////////////////////////
		//////// ADD POLICIES TO MAIN LISTS
		get_monotonic_time(&tsm);
		int s = 0;
		for (s = 0; s < NPOLICIES; s++) {
			// add residue to list
			cons_res.step = instep;
			cons_res.form = POLICIES[s];
			//printf("before reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			#ifdef IM_REDUCE
			reduce(instep, &cons_res);
			#endif
			//printf("after reduction, cons_res is (%d,%d)\n", cons_res.step, cons_res.form);
			rbInsert(&mainresbuf[s], cons_res.step, cons_res.form);
			//printf("added (%d,%d) to ring\n", cons_res.step, cons_res.form);
		}
		get_monotonic_time(&tem);
		nt_polinc += get_elapsed_ltime(&tsm, &tem);
		/////////////////////////////////////////////////


		////////////////////////////////////////////////
		///////// CONSERVATIVE CHECK
		get_monotonic_time(&tsm);
		#ifdef MON_CONS
		for (s = 0; s < NPOLICIES; s++) {
			checkConsStep(&mainresbuf[s]);
		//checkConsStepLoop();
		}
		#endif
		get_monotonic_time(&tem);
		nt_cons += get_elapsed_ltime(&tsm, &tem);
		///////////////////////////////////////////////
	
		
		/////////////////////////////////////////////////////////
		/////////// AGGRESSIVE CHECK
		get_monotonic_time(&tsm);
		#ifdef MON_AGGR
		for (s = 0; s < NPOLICIES; s++) {
			start = mainresbuf[s].start;
			end = mainresbuf[s].end;
			while (start != end) {
				resp = rbGet(&mainresbuf[s], start);
				reduce(instep, resp);
				//printf("in step: %d, reduced %d to %d\n", instep, resp->step, resp->form);
				if (resp->form == FORM_TRUE) {
					//printf("step %d is TRUE\n", resp->step);
					rbSafeRemove(&mainresbuf[s], start);
					stepSatisfy();
				} else if (resp->form == FORM_FALSE) {
					//printf("step %d is FALSE\n", resp->step);
					rbSafeRemove(&mainresbuf[s], start);
					traceViolate();
				} 
				start = (start + 1) % mainresbuf[s].size;
			}
		}
		#endif
		get_monotonic_time(&tem);
		nt_aggr += get_elapsed_ltime(&tsm, &tem);
		/////////////// END AGGRESSIVE CHECK ////////////////////

		
		//get_monotonic_time(&tem);
		stepcount = stepcount + 1;
		//printf("TIMES: incr: %09lu, policy: %09lu, cons: %09lu, aggr: %09lu, steps: %09lu\n", nt_incr, nt_polinc, nt_cons, nt_aggr, stepcount);
	}
	get_monotonic_time(&total_tem);
	////////////////////////////////////////////////
	// FINISHED CHECKING, print stats
	printf("numreduces = %d\n", numreduces);
	printf("TIMES: total: %09lu, incr: %09lu, policy: %09lu, cons: %09lu, aggr: %09lu, steps: %lu\n", get_elapsed_ltime(&total_tsm,&total_tem), nt_incr, nt_polinc, nt_cons, nt_aggr, stepcount);
	printf("Trace finished. Satisfied is %s\n", tracesat ? "true" : "false");
	#ifdef __MACH__
  	mach_port_deallocate(mach_task_self(), cclock);
	#endif
} // END MAIN



void traceViolate() {
	printf("Trace VIOLATED!!! @ %d\n",instep);
	tracesat = 0;
}
void stepSatisfy() {
	// do nothing...	
}
void traceFail() {
	printf("FAILED REDUCE\n");
	exit(-2);
}
