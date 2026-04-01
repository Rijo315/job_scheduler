import heapq
import random
import copy
from dataclasses import dataclass
from typing import List,Tuple,Optional
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
class Algorithm(Enum):
    FCFS="First Come First Serve"
    SJF="Shortest Job First (Non-preemptive)"
    SRTF="Shortest Remaining Time First (Preemptive)"
    PRIORITY_NP="Priority Scheduling (Non-preemptive)"
    PRIORITY_P="Priority Scheduling (Preemptive)"
    ROUND_ROBIN="Round Robin"
@dataclass
class Job:
    id:int
    arrival_time:int
    burst_time:int
    priority:int=0
    remaining_time:int=None
    start_time:int=-1
    completion_time:int=0
    waiting_time:int=0
    turnaround_time:int=0
    response_time:int=0   
    def __post_init__(self):
        if self.remaining_time is None:
            self.remaining_time=self.burst_time
    
    def __lt__(self,other):
        return self.priority<other.priority
class JobScheduler:
    def __init__(self):
        self.jobs=[]
        self.algorithm=None
        self.time_quantum=2   
    def add_job(self,job:Job):
        self.jobs.append(job)      
    def generate_random_jobs(self,n:int,max_arrival:int=20,max_burst:int=15):
        self.jobs=[]
        for i in range(n):
            arrival=random.randint(0,max_arrival)
            burst=random.randint(1,max_burst)
            priority=random.randint(1,5)
            self.jobs.append(Job(i+1,arrival,burst,priority))     
    def reset_jobs(self):
        for job in self.jobs:
            job.remaining_time=job.burst_time
            job.start_time=-1
            job.completion_time=0
            job.waiting_time=0
            job.turnaround_time=0
            job.response_time=0        
    def fcfs(self)->List[Tuple[int,int,int]]:
        timeline=[]
        current_time=0
        sorted_jobs=sorted(self.jobs,key=lambda x:x.arrival_time)
        for job in sorted_jobs:
            if current_time<job.arrival_time:
                current_time=job.arrival_time
            job.start_time=current_time
            job.completion_time=current_time+job.burst_time
            job.turnaround_time=job.completion_time-job.arrival_time
            job.waiting_time=job.turnaround_time-job.burst_time
            job.response_time=job.start_time-job.arrival_time
            timeline.append((job.id,current_time,job.completion_time))
            current_time+=job.burst_time  
        return timeline
    def sjf(self)->List[Tuple[int,int,int]]:
        timeline=[]
        current_time=0
        remaining_jobs=sorted(self.jobs,key=lambda x:x.arrival_time)
        completed=0
        ready_queue=[]
        while completed<len(self.jobs):
            while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
                job=remaining_jobs.pop(0)
                heapq.heappush(ready_queue,(job.burst_time,job.id,job))
            if ready_queue:
                burst,_,job=heapq.heappop(ready_queue)
                if current_time<job.arrival_time:
                    current_time=job.arrival_time
                job.start_time=current_time
                job.completion_time=current_time+job.burst_time
                job.turnaround_time=job.completion_time-job.arrival_time
                job.waiting_time=job.turnaround_time-job.burst_time
                job.response_time=job.start_time-job.arrival_time
                timeline.append((job.id,current_time,job.completion_time))
                current_time+=job.burst_time
                completed+=1
            else:
                if remaining_jobs:
                    current_time=remaining_jobs[0].arrival_time            
        return timeline
    def srtf(self)->List[Tuple[int,int,int]]:
        timeline=[]
        current_time=0
        remaining_jobs=sorted(self.jobs,key=lambda x:x.arrival_time)
        ready_queue=[]
        current_job=None
        current_start=None
        completed=0
        for job in self.jobs:
            job.remaining_time=job.burst_time
        while completed<len(self.jobs):
            while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
                job=remaining_jobs.pop(0)
                heapq.heappush(ready_queue,(job.remaining_time,job.id,job))
            if ready_queue:
                remaining,_,next_job=heapq.heappop(ready_queue)
                if current_job and current_job!=next_job:
                    if current_start is not None:
                        timeline.append((current_job.id,current_start,current_time))
                    if current_job and current_job.remaining_time>0:
                        heapq.heappush(ready_queue,(current_job.remaining_time,current_job.id,current_job))
                    current_job=next_job
                    current_start=current_time
                if current_job is None:
                    current_job=next_job
                    current_start=current_time
                if current_job.start_time==-1:
                    current_job.start_time=current_time
                    current_job.response_time=current_job.start_time-current_job.arrival_time
                if remaining_jobs:
                    next_arrival=remaining_jobs[0].arrival_time
                    time_to_next=min(1,next_arrival-current_time)
                else:
                    time_to_next=1
                current_time+=time_to_next
                current_job.remaining_time-=time_to_next
                if current_job.remaining_time==0:
                    current_job.completion_time=current_time
                    current_job.turnaround_time=current_job.completion_time-current_job.arrival_time
                    current_job.waiting_time=current_job.turnaround_time-current_job.burst_time
                    timeline.append((current_job.id,current_start,current_time))
                    completed+=1
                    current_job=None
                    current_start=None
            else:
                if remaining_jobs:
                    current_time=remaining_jobs[0].arrival_time
                else:
                    break            
        return timeline
    def priority_scheduling(self,preemptive:bool=False)->List[Tuple[int,int,int]]:
        timeline=[]
        current_time=0
        remaining_jobs=sorted(self.jobs,key=lambda x:x.arrival_time)
        ready_queue=[]
        completed=0
        current_job=None
        current_start=None
        for job in self.jobs:
            job.remaining_time=job.burst_time
        while completed<len(self.jobs):
            while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
                job=remaining_jobs.pop(0)
                heapq.heappush(ready_queue,(job.priority,job.id,job))
            if ready_queue:
                priority,_,next_job=heapq.heappop(ready_queue) 
                if preemptive and current_job and current_job!=next_job:
                    if current_start is not None:
                        timeline.append((current_job.id,current_start,current_time))
                    if current_job.remaining_time>0:
                        heapq.heappush(ready_queue,(current_job.priority,current_job.id,current_job))
                    current_job=next_job
                    current_start=current_time
                elif not current_job:
                    current_job=next_job
                    current_start=current_time
                elif current_job==next_job:
                    pass
                else:
                    heapq.heappush(ready_queue,(priority,next_job.id,next_job))
                if current_job.start_time==-1:
                    current_job.start_time=current_time
                    current_job.response_time=current_job.start_time-current_job.arrival_time
                if preemptive:
                    current_time+=1
                    current_job.remaining_time-=1
                    if current_job.remaining_time==0:
                        current_job.completion_time=current_time
                        current_job.turnaround_time=current_job.completion_time-current_job.arrival_time
                        current_job.waiting_time=current_job.turnaround_time-current_job.burst_time
                        timeline.append((current_job.id,current_start,current_time))
                        completed+=1
                        current_job=None
                        current_start=None
                else:
                    current_time+=current_job.remaining_time
                    current_job.remaining_time=0
                    current_job.completion_time=current_time
                    current_job.turnaround_time=current_job.completion_time-current_job.arrival_time
                    current_job.waiting_time=current_job.turnaround_time-current_job.burst_time
                    timeline.append((current_job.id,current_start,current_time))
                    completed+=1
                    current_job=None
                    current_start=None
            else:
                if remaining_jobs:
                    current_time=remaining_jobs[0].arrival_time
                else:
                    break
                    
        return timeline
    
    def round_robin(self)->List[Tuple[int,int,int]]:
        timeline=[]
        current_time=0
        ready_queue=[]
        remaining_jobs=sorted(self.jobs,key=lambda x:x.arrival_time)
        
        for job in self.jobs:
            job.remaining_time=job.burst_time
        
        while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
            job=remaining_jobs.pop(0)
            ready_queue.append(job)
        current_job=None
        current_start=None
        while ready_queue or remaining_jobs:
            if not current_job and ready_queue:
                current_job=ready_queue.pop(0)
                current_start=current_time
                if current_job.start_time==-1:
                    current_job.start_time=current_time
                    current_job.response_time=current_job.start_time-current_job.arrival_time
            if current_job:
                execute_time=min(self.time_quantum,current_job.remaining_time)
                current_time+=execute_time
                current_job.remaining_time-=execute_time
                while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
                    ready_queue.append(remaining_jobs.pop(0))
                if current_job.remaining_time==0:
                    current_job.completion_time=current_time
                    current_job.turnaround_time=current_job.completion_time-current_job.arrival_time
                    current_job.waiting_time=current_job.turnaround_time-current_job.burst_time
                    timeline.append((current_job.id,current_start,current_time))
                    current_job=None
                else:
                    timeline.append((current_job.id,current_start,current_time))
                    ready_queue.append(current_job)
                    current_job=None
            else:
                if remaining_jobs:
                    current_time=remaining_jobs[0].arrival_time
                    while remaining_jobs and remaining_jobs[0].arrival_time<=current_time:
                        ready_queue.append(remaining_jobs.pop(0))
        return timeline
    def schedule(self,algorithm:Algorithm)->Tuple[List[Tuple[int,int,int]],dict]:
        self.reset_jobs()
        self.algorithm=algorithm
        if algorithm==Algorithm.FCFS:
            timeline=self.fcfs()
        elif algorithm==Algorithm.SJF:
            timeline=self.sjf()
        elif algorithm==Algorithm.SRTF:
            timeline=self.srtf()
        elif algorithm==Algorithm.PRIORITY_NP:
            timeline=self.priority_scheduling(preemptive=False)
        elif algorithm==Algorithm.PRIORITY_P:
            timeline=self.priority_scheduling(preemptive=True)
        elif algorithm==Algorithm.ROUND_ROBIN:
            timeline=self.round_robin()
        else:
            raise ValueError("Unknown algorithm")
        metrics=self.calculate_metrics()
        return timeline,metrics
    def calculate_metrics(self)->dict:
        n=len(self.jobs)
        total_turnaround=sum(j.turnaround_time for j in self.jobs)
        total_waiting=sum(j.waiting_time for j in self.jobs)
        total_response=sum(j.response_time for j in self.jobs)
        total_burst=sum(j.burst_time for j in self.jobs)
        total_time=max(j.completion_time for j in self.jobs)
        cpu_utilization=(total_burst/total_time)*100 if total_time>0 else 0
        throughput=n/total_time if total_time>0 else 0
        return {
            'avg_turnaround_time':total_turnaround/n,
            'avg_waiting_time':total_waiting/n,
            'avg_response_time':total_response/n,
            'cpu_utilization':cpu_utilization,
            'throughput':throughput,
            'total_time':total_time
        }
    def display_results(self,algorithm:Algorithm):
        timeline,metrics=self.schedule(algorithm)
        print(f"\n{'='*60}")
        print(f"Algorithm: {algorithm.value}")
        print(f"{'='*60}")
        print(f"{'Job':<6} {'Arrival':<10} {'Burst':<8} {'Priority':<10} {'Start':<8} {'Complete':<10} {'Turnaround':<12} {'Waiting':<10} {'Response':<10}")
        print(f"{'-'*95}")
        for job in sorted(self.jobs,key=lambda x:x.id):
            print(f"{job.id:<6} {job.arrival_time:<10} {job.burst_time:<8} {job.priority:<10} "
                  f"{job.start_time:<8} {job.completion_time:<10} {job.turnaround_time:<12} "
                  f"{job.waiting_time:<10} {job.response_time:<10}")
        print(f"\n{'Performance Metrics':^60}")
        print(f"{'-'*60}")
        print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
        print(f"Average Waiting Time:     {metrics['avg_waiting_time']:.2f}")
        print(f"Average Response Time:    {metrics['avg_response_time']:.2f}")
        print(f"CPU Utilization:          {metrics['cpu_utilization']:.2f}%")
        print(f"Throughput:               {metrics['throughput']:.3f} jobs/unit time")
        print(f"Total Execution Time:     {metrics['total_time']}")
        return timeline,metrics
    def visualize_timeline(self,timeline:List[Tuple[int,int,int]],algorithm:Algorithm):
        fig,ax=plt.subplots(figsize=(12,6))
        colors=plt.cm.Set3(np.linspace(0,1,len(self.jobs)))
        job_colors={job.id:colors[i] for i,job in enumerate(self.jobs)}
        y_position=1
        y_height=0.8
        for job_id,start,end in timeline:
            duration=end-start
            ax.barh(y_position,duration,left=start,height=y_height,
                   color=job_colors[job_id],edgecolor='black',linewidth=1)
            ax.text(start+duration/2,y_position,f'P{job_id}',
                   ha='center',va='center',fontsize=10,fontweight='bold')
        for job in self.jobs:
            ax.plot(job.arrival_time,y_position+0.4,'rv',markersize=8,
                   label=f'P{job.id} arrival' if job.id==1 else "")
        ax.set_xlabel('Time',fontsize=12)
        ax.set_ylabel('CPU',fontsize=12)
        ax.set_title(f'CPU Scheduling Timeline - {algorithm.value}',fontsize=14,fontweight='bold')
        ax.set_ylim(0.5,1.5)
        ax.grid(True,axis='x',alpha=0.3)
        patches=[mpatches.Patch(color=job_colors[job.id],label=f'P{job.id}')
                for job in self.jobs[:5]]
        ax.legend(handles=patches,loc='upper right') 
        plt.tight_layout()
        plt.show()
    def compare_algorithms(self):
        results={}
        for algo in Algorithm:
            timeline,metrics=self.schedule(algo)
            results[algo.value]=metrics    
        print(f"\n{'='*80}")
        print(f"{'Algorithm Comparison':^80}")
        print(f"{'='*80}")
        print(f"{'Algorithm':<35} {'Avg Turnaround':<18} {'Avg Waiting':<15} {'CPU Util':<12} {'Throughput':<12}")
        print(f"{'-'*80}")
        for algo_name,metrics in results.items():
            print(f"{algo_name:<35} {metrics['avg_turnaround_time']:<18.2f} "
                  f"{metrics['avg_waiting_time']:<15.2f} "
                  f"{metrics['cpu_utilization']:<12.2f}% "
                  f"{metrics['throughput']:<12.3f}")
        return results
def main():
    scheduler=JobScheduler()
    while True:
        print("\n"+"="*50)
        print("JOB SCHEDULING SIMULATOR")
        print("="*50)
        print("1. Add Job Manually")
        print("2. Generate Random Jobs")
        print("3. Display Jobs")
        print("4. Run Single Algorithm")
        print("5. Compare All Algorithms")
        print("6. Visualize Timeline")
        print("7. Exit")
        choice=input("\nEnter your choice (1-7): ")
        if choice=='1':
            try:
                job_id=len(scheduler.jobs)+1
                arrival=int(input("Arrival Time: "))
                burst=int(input("Burst Time: "))
                priority=int(input("Priority (1-5, 1=highest): "))
                scheduler.add_job(Job(job_id,arrival,burst,priority))
                print(f"Job {job_id} added successfully!")
            except ValueError:
                print("Invalid input! Please enter numbers only.")        
        elif choice=='2':
            try:
                n=int(input("Number of jobs to generate: "))
                max_arrival=int(input("Max arrival time (default 20): ") or 20)
                max_burst=int(input("Max burst time (default 15): ") or 15)
                scheduler.generate_random_jobs(n,max_arrival,max_burst)
                print(f"{n} random jobs generated!")
            except ValueError:
                print("Invalid input!")        
        elif choice=='3':
            if not scheduler.jobs:
                print("No jobs to display. Add jobs first!")
            else:
                print(f"\n{'ID':<6} {'Arrival':<10} {'Burst':<8} {'Priority':<10}")
                print("-"*35)
                for job in scheduler.jobs:
                    print(f"{job.id:<6} {job.arrival_time:<10} {job.burst_time:<8} {job.priority:<10}")       
        elif choice=='4':
            if not scheduler.jobs:
                print("No jobs to schedule. Add jobs first!")
                continue   
            print("\nSelect Algorithm:")
            for i,algo in enumerate(Algorithm,1):
                print(f"{i}. {algo.value}")
            try:
                algo_choice=int(input("Enter algorithm number: "))
                algo=list(Algorithm)[algo_choice-1]
                if algo==Algorithm.ROUND_ROBIN:
                    quantum=input("Enter time quantum (default 2): ")
                    if quantum:
                        scheduler.time_quantum=int(quantum)
                scheduler.display_results(algo)
                vis=input("\nVisualize timeline? (y/n): ").lower()
                if vis=='y':
                    timeline,_=scheduler.schedule(algo)
                    scheduler.visualize_timeline(timeline,algo)    
            except (ValueError,IndexError):
                print("Invalid choice!")    
        elif choice=='5':
            if not scheduler.jobs:
                print("No jobs to schedule. Add jobs first!")
            else:
                scheduler.compare_algorithms()   
        elif choice=='6':
            if not scheduler.jobs:
                print("No jobs to schedule. Add jobs first!")
                continue    
            print("\nSelect Algorithm to Visualize:")
            for i,algo in enumerate(Algorithm,1):
                print(f"{i}. {algo.value}")
            try:
                algo_choice=int(input("Enter algorithm number: "))
                algo=list(Algorithm)[algo_choice-1]
                timeline,_=scheduler.schedule(algo)
                scheduler.visualize_timeline(timeline,algo)
            except (ValueError,IndexError):
                print("Invalid choice!")    
        elif choice=='7':
            print("Exiting simulator. Goodbye!")
            break    
        else:
            print("Invalid choice! Please enter 1-7.")

if __name__=="__main__":
    main()