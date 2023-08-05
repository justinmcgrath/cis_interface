

disp('maxMsgSrv(M): Hello!');

rpc = CisInterface('CisRpcServer', 'maxMsgSrv', '%s', '%s');

while (1)
  [flag, vars] = rpc.recv();
  if (~flag)
    break;
  end
  fprintf('maxMsgSrv(M): rpcRecv returned %d, input %.10s...\n', ...
	  flag, char(vars{1}));
  rpc.send(vars{1});
end

disp('maxMsgSrv(M): Goodbye!');

