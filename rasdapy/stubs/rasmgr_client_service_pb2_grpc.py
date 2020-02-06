# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from rasdapy.stubs import rasmgr_client_service_pb2 as rasmgr__client__service__pb2, common_service_pb2 as common__service__pb2


class RasmgrClientServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Connect = channel.unary_unary(
        '/rasnet.service.RasmgrClientService/Connect',
        request_serializer=rasmgr__client__service__pb2.ConnectReq.SerializeToString,
        response_deserializer=rasmgr__client__service__pb2.ConnectRepl.FromString,
        )
    self.Disconnect = channel.unary_unary(
        '/rasnet.service.RasmgrClientService/Disconnect',
        request_serializer=rasmgr__client__service__pb2.DisconnectReq.SerializeToString,
        response_deserializer=common__service__pb2.Void.FromString,
        )
    self.OpenDb = channel.unary_unary(
        '/rasnet.service.RasmgrClientService/OpenDb',
        request_serializer=rasmgr__client__service__pb2.OpenDbReq.SerializeToString,
        response_deserializer=rasmgr__client__service__pb2.OpenDbRepl.FromString,
        )
    self.CloseDb = channel.unary_unary(
        '/rasnet.service.RasmgrClientService/CloseDb',
        request_serializer=rasmgr__client__service__pb2.CloseDbReq.SerializeToString,
        response_deserializer=common__service__pb2.Void.FromString,
        )
    self.KeepAlive = channel.unary_unary(
        '/rasnet.service.RasmgrClientService/KeepAlive',
        request_serializer=rasmgr__client__service__pb2.KeepAliveReq.SerializeToString,
        response_deserializer=common__service__pb2.Void.FromString,
        )


class RasmgrClientServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Connect(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Disconnect(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OpenDb(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CloseDb(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def KeepAlive(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RasmgrClientServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Connect': grpc.unary_unary_rpc_method_handler(
          servicer.Connect,
          request_deserializer=rasmgr__client__service__pb2.ConnectReq.FromString,
          response_serializer=rasmgr__client__service__pb2.ConnectRepl.SerializeToString,
      ),
      'Disconnect': grpc.unary_unary_rpc_method_handler(
          servicer.Disconnect,
          request_deserializer=rasmgr__client__service__pb2.DisconnectReq.FromString,
          response_serializer=common__service__pb2.Void.SerializeToString,
      ),
      'OpenDb': grpc.unary_unary_rpc_method_handler(
          servicer.OpenDb,
          request_deserializer=rasmgr__client__service__pb2.OpenDbReq.FromString,
          response_serializer=rasmgr__client__service__pb2.OpenDbRepl.SerializeToString,
      ),
      'CloseDb': grpc.unary_unary_rpc_method_handler(
          servicer.CloseDb,
          request_deserializer=rasmgr__client__service__pb2.CloseDbReq.FromString,
          response_serializer=common__service__pb2.Void.SerializeToString,
      ),
      'KeepAlive': grpc.unary_unary_rpc_method_handler(
          servicer.KeepAlive,
          request_deserializer=rasmgr__client__service__pb2.KeepAliveReq.FromString,
          response_serializer=common__service__pb2.Void.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'rasnet.service.RasmgrClientService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
