function plot_bands
%read in EIGENVAL file
%Enter ticks as string, e.g. 'W L g X W K M g'
%Lowercase g for gamma
outcar=fopen('OUTCAR', 'r');
temp=fgetl(outcar);
flag=1;
while flag
    if (size(temp,2)<18)
        temp=fgetl(outcar);
    elseif (strcmp(temp(1:18),'  volume of cell :'))
        flag=0;
    else
        temp=fgetl(outcar);
    end
end
len=size(temp,2);
volume=str2num(temp(19:len));

%now getting fermi energy
temp=fgetl(outcar);
while ~feof(outcar)
    if (size(temp,2)<8)
        temp=fgetl(outcar);
    elseif (strcmp(temp(1:8),' E-fermi'))
        fermi_energy=str2num(temp(11:19));
        temp=fgetl(outcar);
    else
        temp=fgetl(outcar);
    end
end
fclose(outcar);

eigenval=fopen('EIGENVAL','r');
buffer=fscanf(eigenval, '%d',4);  %reading the first line  
ispin=buffer(4); %4th number is ispin (ispin =1: non-magnetic calculation, ispin=2: magnetic)    c)

for i=1:5  %passing 4 lines of unimportant data (unimportant for our current goal)
    fgetl(eigenval);
end
temp=fscanf(eigenval,'%d');
num_kpoints=temp(2);    %number of kpoints
num_energies=temp(3);   % number of energy states (total bands)
valence_num=temp(1)/2;  % number of valence bands (1st element is number of valence electrons)
% therefore: number of conduction bands= total bands - valence bands
% =(num_energies-valence_num)
if ispin==2 ne=temp(1)
    VBM=ne;
    energies=zeros(num_kpoints, num_energies*2);
else
    VBM=ceil(valence_num);
    energies=zeros(num_kpoints, num_energies);
end
kpoints=zeros(num_kpoints,3); % 3 for their coordinates
kpoint_wts=zeros(num_kpoints,1);


if ispin==1
for i=1:num_kpoints
    temp=fscanf(eigenval, '%e',4);
    kpoints(i,1)=temp(1);
    kpoints(i,2)=temp(2);
    kpoints(i,3)=temp(3);
    kpoint_wts(i)=temp(4);
    for j=1:num_energies
        temp=fscanf(eigenval,'%d %f',2);
        energies(i,j)=temp(2);  % energy of j band in kpoint #i
     %   if j>valence_num                        % % % manual band gap increase
    %        energies(i,j)=energies(i,j)+0.6;    % % % manual band gap increase
    %    end                                     % % % manual band gap increase
    end
end
end

%%% this section is only for spin-polarized (ispin=2) calculation
if ispin==2
for i=1:num_kpoints
    temp=fscanf(eigenval, '%e',4);
    kpoints(i,1)=temp(1);
    kpoints(i,2)=temp(2);
    kpoints(i,3)=temp(3);
    kpoint_wts(i)=temp(4);
    for j=1:num_energies
        temp=fscanf(eigenval,'%d %f %f',3);
  %      if j<valence_num+1
  %          if temp(2)>temp(3)
  %              energies(i,j)=temp(2);
   %         else
  %              energies(i,j)=temp(3);
  %          end
 %       end
  %      if j>valence_num
   %         if temp(2)>temp(3)
   %             energies(i,j)=temp(3);
  %          else
   %             energies(i,j)=temp(2);
   %         end
%        end
energies(i,(j-1)*2+1)=temp(2);
energies(i,j*2)=temp(3);
    end
end
end
%%% end of ispin=2 reading

x_axis=zeros(num_kpoints,1);
offset=0;
%HSEweight1kpoints=0;%424;%%%%%%%%%%%%%%%%%%%%%
HSEweight1kpoints=0;
for i=2+HSEweight1kpoints:num_kpoints  %if you are using explicit kpoints for HSE set the first number as 2+(number of nonzero weight kpoints)
    x_axis(i)=offset+sqrt((kpoints(i-1,1)-kpoints(i,1))^2+(kpoints(i-1,2)-kpoints(i,2))^2+(kpoints(i-1,3)-kpoints(i,3))^2);
    offset=offset+sqrt((kpoints(i-1,1)-kpoints(i,1))^2+(kpoints(i-1,2)-kpoints(i,2))^2+(kpoints(i-1,3)-kpoints(i,3))^2);
end
x_axis1=x_axis(1+HSEweight1kpoints:num_kpoints,1);
energies2=energies(1+HSEweight1kpoints:num_kpoints,:);
s=size(x_axis1);
s(1);
%--- begin Deko's edits
tick1_list = 'g H N P g N';
tick1_list = strrep(tick1_list,' ','');
tick_list = {};
number_of_kpoints=length(tick1_list); %%%%%%%%%%%%%%%%%


for i=1:length(tick1_list)
    tick_list(i)={tick1_list(i)};
end

for i=1:length(tick_list)
    if strcmp(tick_list(i),'g')
        tick_list(i)={'\Gamma'};
    end
    tick_list(i)=strcat('$',tick_list(i),'$');
end
%--- end Deko's edits
intervals=s(1)/(number_of_kpoints-1);

%%%%%%%%%%%%%%%%%%%%%%%%%%%% *** PLOTTING INPUTS **** %%%%%%%%%%%%%
linewidth=1.2;
fontsize=18;
x_axis1
energies2
% hold on
% if ispin==1
%    for i=1:size(energies,2)%num_energies*2
%     plot(x_axis1,energies2(:,i)-fermi_energy,'Linewidth',linewidth);%,'b+');%-fermi_energy);
%    end 
% else
%     for i=1:size(energies,2)%num_energies*2
%         if floor(i/2)==i/2
%     plot(x_axis1,energies2(:,i)-fermi_energy,'--r','Linewidth',linewidth);%,'b+');%-fermi_energy);
%         else
%     plot(x_axis1,energies2(:,i)-fermi_energy,'Linewidth',linewidth);%,'b+');%-fermi_energy);
%         end
%    end 
%     
% end
% 
% grid on
% set(gca,'FontSize',fontsize,'FontWeight','b');
% ylabel('energy (eV)','FontSize',fontsize+4,'FontWeight','b','Interpreter','Latex','FontName','Times New Roman');%,'Position',[-.2,0.1])
% axis_label_indices=zeros(number_of_kpoints,1);
% axis_label_indices(1)=x_axis1(1);
% for i=1:number_of_kpoints-1
%     axis_label_indices(i+1)=x_axis1(i*intervals);
% end
% ylim([-4 6]);
% xlim([min(x_axis),max(x_axis)]);
% set(gca,'XTick',axis_label_indices,'FontSize',fontsize,'FontWeight','b','FontName','Times New Roman','box','on')
% %format_ticks(gca,tick_list,{});%{'$-2$','$-1$','$0$','$1$','$2$'});
% %Note- format_ticks edited by Deko
% hold off
%figure(2)
%hold on
%x_axis_alt=1:num_kpoints;
%for i=1:num_energies
%    plot(x_axis_alt,energies(:,i),'r');
%end
%hold off
fclose(eigenval);
save axis.mat x_axis1
save bands.mat energies2
