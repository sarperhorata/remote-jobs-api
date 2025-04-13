import { UseQueryOptions } from 'react-query';

declare module 'react-query' {
  export function useQuery<
    TQueryFnData = unknown,
    TError = unknown,
    TData = TQueryFnData,
    TQueryKey extends QueryKey = QueryKey
  >(
    queryKey: TQueryKey,
    queryFn: QueryFunction<TQueryFnData, TQueryKey>,
    options?: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>
  ): QueryResult<TData, TError>;
} 