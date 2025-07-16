import { getApiUrl } from '../../utils/apiConfig';

describe('APIHelpers', () => {
  test('getApiUrl returns a valid URL', async () => {
    const apiUrl = await getApiUrl();
    expect(apiUrl).toBeDefined();
    expect(typeof apiUrl).toBe('string');
    expect(apiUrl).toContain('http');
  });
});
