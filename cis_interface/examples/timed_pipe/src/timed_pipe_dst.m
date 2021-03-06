disp('Hello from Matlab pipe_dst');

% Ins/outs matching with the the model yaml
inq = CisInterface('CisInput', 'input_pipe');
outf = CisInterface('CisOutput', 'output_file');
disp('pipe_dst(M): Created I/O channels');

% Continue receiving input from the queue
count = 0;
while (1);
  [flag, buf] = inq.recv();
  if (~flag);
    disp('pipe_dst(M): Input channel closed');
    break;
  end;
  ret = outf.send(buf);
  if (~ret);
    fprintf('pipe_dst(M): SEND ERROR ON MSG %d\n', count);
    exit(-1);
  end;
  count = count + 1;
end;

fprintf('Goodbye from Matlab destination. Received %d messages.\n', count);
