/**
 * Поиск категорий по традиции/концепции
 */
async searchCategoriesByTradition(tradition: string): Promise<Category[]> {
  const client = await this.getClient();
  try {
    const result = await client.query(
      `SELECT * FROM categories WHERE tradition_concepts ? $1`,
      [tradition]
    );
    return result.rows;
  } catch (error) {
    logger.error(`Error searching categories by tradition: ${error}`);
    throw new Error(`Failed to search categories by tradition: ${error}`);
  } finally {
    client.release();
  }
}

/**
 * Поиск категорий по философу
 */
async searchCategoriesByPhilosopher(philosopher: string): Promise<Category[]> {
  const client = await this.getClient();
  try {
    const result = await client.query(
      `SELECT * FROM categories WHERE philosophers ? $1`,
      [philosopher]
    );
    return result.rows;
  } catch (error) {
    logger.error(`Error searching categories by philosopher: ${error}`);
    throw new Error(`Failed to search categories by philosopher: ${error}`);
  } finally {
    client.release();
  }
}